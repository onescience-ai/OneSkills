# Pre-Execution Dependency Checklist

本文档定义 orchestrator 在 Global Plan 中为长时间运行任务插入"执行前依赖预检"步骤的标准流程。预检步骤必须在主执行步骤之前完成，预检通过后方可执行主任务。

## 1. 何时需要执行前预检

当 Global Plan 中的某个步骤同时满足以下任一条件时，必须在其之前插入预检步骤：

- 任务涉及调用 GPU 推理或训练
- 任务涉及使用 conda 虚拟环境中的 Python 包
- 任务在远程主机（SSH/SLURM/SCnet）上运行
- 任务预计运行时间 > 10 分钟

## 2. 预检项目清单

预检步骤为 `orchestrator_step`，使用 Bash 工具执行。检查内容根据任务类型选择性执行：

### 2.1 Python 模块导入检查

**适用场景**：任务入口脚本依赖特定 Python 包或模块。

```bash
# 方法 1：直接导入检查
python -c "import <模块名>; print('<模块名> import OK')"

# 方法 2：通过 conda 环境导入
conda run -n <env_name> python -c "import <模块名>; print('<模块名> import OK')"
```

**参考案例**：
- `bionemo.evo2.lightning` 缺失 → 在实际推理中发现模块导入失败后才报错
- `causal_conv1d` 缺失 → 模型加载完成后才报错，浪费了加载时间
- 若在预检阶段就能发现，可直接跳过模型加载，节省时间
- 正确的预检命令：
  ```bash
  conda run -n bioscience-evo2 python -c "from bionemo.evo2.lightning import batch_collator; print('OK')"
  conda run -n bioscience-evo2 python -c "import causal_conv1d; print('OK')"
  ```

### 2.2 CUDA 扩展可用性检查

**适用场景**：任务使用 GPU 且依赖 CUDA 编译扩展。

```bash
# 检查 torch CUDA 可用
python -c "import torch; assert torch.cuda.is_available(), 'CUDA not available'; print(f'CUDA OK, device count: {torch.cuda.device_count()}')"

# 检查具体 CUDA 扩展
python -c "import <cuda_extension>; print('<cuda_extension> OK')"
```

**参考案例**：
- `causal_conv1d` 是 Hyena 模型的 CUDA 扩展，在模型加载完成后才被调用
- 若未预检，模型加载完成后才发现缺失，浪费了加载时间
- 若在预检阶段就能发现，可直接跳过模型加载，节省时间

### 2.3 入口脚本语法检查

**适用场景**：任务入口脚本是新生成或修改过的。

```bash
# 语法编译检查（不实际执行）
python -c "import py_compile; py_compile.compile('<脚本路径>', doraise=True); print('Syntax OK')"
```

### 2.4 环境依赖一致性检查

**适用场景**：任务使用 conda 或 pip 环境。

```bash
# pip 依赖一致性检查
pip check

# conda 环境包清单（确认包存在）
conda run -n <env_name> pip list | grep <关键包名>
```

### 2.5 GPU 可访问性检查

**适用场景**：任务需要 GPU。

```bash
# GPU 基本信息
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}, Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"

# GPU 数量
python -c "import torch; print(f'GPU count: {torch.cuda.device_count()}')"
```

### 2.6 必要数据文件存在性检查

**适用场景**：任务依赖输入数据文件。

```bash
# 检查文件是否存在
ls -la <文件路径>

# 或通过 Bash 直接检查
test -f <文件路径> && echo "EXISTS" || echo "MISSING"
```

### 2.7 GPU 显存预算估算

**适用场景**：任务涉及 GPU 推理或训练，且模型/输入规模较大（如蛋白质结构预测、大语言模型推理、长序列处理）。

当任务属于 `onescience-infer` 或 `onescience-trainer` 管理的 GPU 密集型任务时，必须执行显存预算估算。详细策略见对应技能中的 `gpu-oom-handling.md`：

1. **估算模型权重显存**：
   - 参数量 × bytes_per_element（float32=4, float16=2）
   - 验证方式：检查 checkpoint 文件大小
   ```bash
   du -sh <checkpoint_path>
   ```

2. **估算输入数据显存**：
   - tokens × dimensions × bytes_per_element
   - 对于蛋白质结构预测：num_tokens × token_dim × 4

3. **估算中间激活显存**：
   - 模型权重显存的 2-5 倍
   - 若有 recycles 参数：× (1 + num_recycles × 0.3)

4. **估算结果物化显存**：
   - 输出张量大小 × 2.0（Python 内存拷贝开销）

5. **总估算与可用显存对比**：
   ```bash
   nvidia-smi --query-gpu=index,memory.total,memory.free --format=csv,noheader
   ```

6. **风险判定**：
   | 总估算 / 单卡可用显存 | 风险等级 | 处理方式 |
   |---|---|---|
   | < 60% | 低风险 | 正常执行 |
   | 60%-80% | 中风险 | 在 Global Plan 中标记需启用内存优化参数 |
   | 80%-95% | 高风险 | 在 Global Plan 中插入低内存配置步骤（最小 recycles、分段物化） |
   | > 95% | 单卡超限 | 不阻断——进入多卡聚合判断（步骤 7） |

7. **多卡聚合判断**（仅当单卡超限时执行）：
   - 确认任务是否支持多 seed 并行（检查推理入口是否有 `--seed` 参数）
   - 若支持：计算最低配置下每张卡是否可容纳单任务
     - `task_memory_low = model + base_activation × 1.3 + materialization × 0.5`
   - 筛选可行 GPU：
     ```bash
     nvidia-smi --query-gpu=index,memory.free --format=csv,noheader | \
       awk -F', ' -v t=<threshold> '{if($2>t) print "GPU "$1" feasible"}'
     ```
   - 决策：
     | 可行 GPU 数 | 决策 | Global Plan 调整 |
     |---|---|---|
     | 0 | 阻断 | `blocking_reason=gpu_oom_all_gpus_insufficient` |
     | 1 | 单卡低内存模式 | 插入 `num_recycles=1` + 分段物化步骤 |
     | >=2 | 多卡多 seed 并行 | 插入多 seed 并行调度步骤，`num_seeds = feasible_gpus`（不做人为截断） |
   - 若任务不支持多 seed：按原单卡超限处理，阻断并建议降低输入规模

估算结果写入预检报告中的 `gpu_memory_budget` 字段。

**参考案例**：
- AlphaFold 3 7PNM (5337 tokens, 10 recycles)：推理 35 GiB + 物化 69 GiB，单卡需求 104 GiB > 可用 83 GiB → 单卡超限。多卡聚合：最低配置 ~74 GiB/卡 < 83 GiB，8 张卡均可行 → 自动启用 8 seed 多卡并行。
- Evo 2 SAE (100k tokens, FFT 计算)：单次 FFT 需要巨大中间内存。若预检阶段完成估算，可自动选择分块处理策略（chunk_size=8192）。

## 3. 预检失败处理流程

### 3.1 失败分类

| 失败类型 | 判定条件 | 处理方式 |
|----------|----------|----------|
| 缺失 Python 包 | `ModuleNotFoundError` | 在 Global Plan 中插入 `pip install` 修复步骤 |
| 缺失 CUDA 扩展 | `ImportError` + CUDA 相关 | 在 Global Plan 中插入源码编译安装步骤 |
| 缺失数据文件 | 文件不存在 | 在 Global Plan 中插入下载/定位步骤 |
| 权限问题 | `PermissionError` / `Access denied` | 阻断并告知用户，要求用户授权或调整 |
| GPU 不可用 | `torch.cuda.is_available()=False` | 确认是否需要 GPU；若需要则阻断 |
| 环境不一致 | `pip check` 返回冲突 | 在 Global Plan 中插入 `pip install` 修复冲突 |
| GPU 显存不足（单卡） | 显存预算估算 > 95% 且任务不支持多 seed | 阻断并建议降低输入规模 |
| GPU 显存不足（全部卡） | 多卡聚合后 0 张卡可行 | 阻断，`blocking_reason=gpu_oom_all_gpus_insufficient` |
| GPU 显存高风险（多卡可行） | 多卡聚合后 >=2 张卡可行 | 在 Global Plan 中插入多 seed 并行调度步骤 |

### 3.2 修复步骤插入规则

1. 预检失败后，不立即放弃任务，先分析失败原因
2. 根据失败类型，在 Global Plan 的当前待执行步骤之前，插入对应的修复步骤
3. 修复步骤完成后，重新执行预检；预检通过后方可执行主任务
4. 若修复步骤也失败，记录阻断原因并进入 `blocked` 状态

### 3.3 不应预检的情况

以下情况不应添加预检步骤：
- 任务不涉及 GPU、conda 环境或远程执行
- 任务预计运行时间 < 1 分钟
- 用户明确声明环境已就绪且已知正确
- 任务已经在之前的步骤中验证过环境（避免重复预检）

## 4. 预检步骤在 Global Plan 中的位置

```text
Global Plan:
  Step 1: <前置步骤>
  Step 2: 【预检】执行前依赖检查 (orchestrator_step)
    - 检查内容：Python 模块导入、CUDA 扩展、GPU 状态
    - 预期产物：preflight_check_report
  Step 3: <主执行步骤> (executor_step: onescience-runtime)
    - 前置条件：Step 2 预检通过
    - ...
```

**关键规则**：
- 预检步骤（Step 2）必须是 `orchestrator_step`，使用 Bash 工具
- 主执行步骤（Step 3）的前置条件必须包含"预检通过"
- 若预检失败，在 Step 2 和 Step 3 之间插入修复步骤 Step 2a、Step 2b 等
