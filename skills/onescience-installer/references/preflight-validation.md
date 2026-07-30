# 环境就绪预检验证（Preflight Validation）

当 `installer_reason=preflight_validation` 时，installer 进入纯验证模式：只做环境就绪检查，不做任何安装操作。此模式是 orchestrator 和 runtime 的环境前置检测的统一入口。

## 1. 触发条件

installer 收到以下任一来源的 `installer_reason=preflight_validation` 委托时进入本流程：

- **来自 orchestrator**：Global Plan 中包含长时间运行任务（预估运行时间 > 10 分钟），orchestrator 规划 `executor_step` 委托 installer 做执行前环境预检。
- **来自 runtime**：runtime 在 preflight 阶段将环境就绪检查完整委托给 installer，installer 返回 readiness 结果后再由 runtime 决定是否进入 execute。

## 2. 预检上下文读取

1. 读取根目录 `onescience.json`，获取：
   - `runtime.execution_profile`（`run_site`、`execution_mode`、`access_mode`）
   - `runtime.conda`（`enabled`、`env_name`、`activate_script`）
   - `runtime.target`（硬件类型）
   - `runtime.script.work_dir` / `runtime.script.code_path`
   - `runtime.ssh.*`（远程通道需要）
   - `runtime.cluster.*`（SLURM 通道需要）
2. 从上游 handoff 中获取：
   - `execution_channel`（`local_direct` / `local_slurm` / `ssh_direct` / `ssh_slurm` / `scnet_mcp`）
   - 入口脚本路径
   - 业务依赖列表（如有）

## 3. 预检项目清单

### 3.1 Conda 配置校验

检查 `runtime.conda` 结构是否有效：

- `runtime.conda` 存在且结构完整
- `enabled` 字段已明确设置（`true` 或 `false`）
- `enabled=true` 时 `env_name` 和 `activate_script`（或可据此渲染最小激活命令）齐备
- `enabled=false` 时为明确写出的值，不得将缺失自动解释为 `enabled=false`

### 3.2 Python 解释器检查

**适用场景**：所有通道。

按当前通道在目标环境执行：

```bash
# 本地 / conda 环境
python --version
which python

# conda 环境
conda run -n <env_name> python --version
```

**远程通道**：必须通过 SSH 在远端执行探测，不得用本地结果替代。

### 3.3 核心依赖导入检查

**适用场景**：所有通道。

```bash
# onescience 包
python -c "import onescience; print('onescience import OK')"

# torch 及 CUDA
python -c "import torch; print(f'torch {torch.__version__}, CUDA: {torch.cuda.is_available()}')"

# 业务依赖（从 handoff 中获取列表）
python -c "import <模块名>; print('<模块名> import OK')"
```

**参考案例**：
- `bionemo.evo2.lightning` 缺失 → 在实际推理中发现模块导入失败后才报错
- `causal_conv1d` 缺失 → 模型加载完成后才报错，浪费了加载时间
- 正确做法：在预检阶段提前发现，避免后续步骤浪费时间

### 3.4 CUDA 扩展可用性检查

**适用场景**：任务使用 GPU 且依赖 CUDA 编译扩展。

```bash
# 检查 torch CUDA 可用
python -c "import torch; assert torch.cuda.is_available(), 'CUDA not available'; print(f'CUDA OK, device count: {torch.cuda.device_count()}')"

# 检查具体 CUDA 扩展
python -c "import <cuda_extension>; print('<cuda_extension> OK')"
```

### 3.5 入口脚本检查

**适用场景**：所有通道。

- 入口脚本路径存在且非空
- 语法编译检查（不实际执行）：

```bash
python -c "import py_compile; py_compile.compile('<脚本路径>', doraise=True); print('Syntax OK')"
```

### 3.6 环境依赖一致性检查

**适用场景**：任务使用 conda 或 pip 环境。

```bash
# pip 依赖一致性检查
pip check

# conda 环境包清单（确认包存在）
conda run -n <env_name> pip list | grep <关键包名>
```

### 3.7 GPU 可访问性检查

**适用场景**：任务需要 GPU。

```bash
# GPU 基本信息
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}, Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"N/A\"}')"

# GPU 数量
python -c "import torch; print(f'GPU count: {torch.cuda.device_count()}')"
```

### 3.8 必要数据文件存在性检查

**适用场景**：任务依赖输入数据文件。

```bash
# 检查文件是否存在
test -f <文件路径> && echo "EXISTS" || echo "MISSING"
```

### 3.9 GPU 显存预算估算

**适用场景**：任务涉及 GPU 推理或训练，且模型/输入规模较大（如蛋白质结构预测、大语言模型推理、长序列处理）。

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
   | 60%-80% | 中风险 | 在返回结果中标记需启用内存优化参数 |
   | 80%-95% | 高风险 | 在返回结果中标记低内存配置建议（最小 recycles、分段物化） |
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
     | 可行 GPU 数 | 决策 | 返回建议 |
     |---|---|---|
     | 0 | 阻断 | `blocking_reason=gpu_oom_all_gpus_insufficient` |
     | 1 | 单卡低内存模式 | 建议 `num_recycles=1` + 分段物化 |
     | >=2 | 多卡多 seed 并行 | 建议 `num_seeds = feasible_gpus`（不做人为截断） |
   - 若任务不支持多 seed：按原单卡超限处理，阻断并建议降低输入规模

估算结果写入预检报告中的 `gpu_memory_budget` 字段。

**参考案例**：
- AlphaFold 3 7PNM (5337 tokens, 10 recycles)：推理 35 GiB + 物化 69 GiB，单卡需求 104 GiB > 可用 83 GiB → 单卡超限。多卡聚合：最低配置 ~74 GiB/卡 < 83 GiB，8 张卡均可行 → 建议 8 seed 多卡并行。
- Evo 2 SAE (100k tokens, FFT 计算)：单次 FFT 需要巨大中间内存。若预检阶段完成估算，可建议分块处理策略（chunk_size=8192）。

## 4. 登录节点 vs 计算节点环境区分（SLURM 通道专用）

在 SLURM 集群环境中，登录节点（login node）与计算节点（compute node）的环境通常不同。

### 4.1 核心验证项（必须在登录节点通过）

- Python 解释器存在且可执行
- `import onescience` 成功
- `import torch` 成功（或对应框架）
- conda 环境可激活
- 入口脚本存在

### 4.2 可选验证项（允许在登录节点失败，推迟到计算节点验证）

- 特定的系统级共享库（如 `libmsgpackc.so.2`、`libcudnn.so`、`libnccl.so` 等仅计算节点才有的库）
- GPU 驱动级依赖
- 高速网络库（如 InfiniBand verbs）
- SLURM 作业执行时的实际资源可用性

### 4.3 共享库缺失跳过规则

若在登录节点执行 `conda activate` 或环境验证时，遇到特定共享库缺失导致 `ldconfig` 或 `ldd` 循环扫描：
- 记录该库缺失为 `warning`（非 `error`），不阻塞预检
- 将缺失的库列表写入 `preflight_result.missing_libs_on_login_node`
- 设置 `preflight_result.deferred_lib_checks=true`，表示库依赖完整性将在计算节点执行时由作业脚本自检
- **禁止**在登录节点为查找特定 `.so` 文件而遍历整个文件系统
- 已知登录节点不可用的库白名单（匹配到后直接跳过不检索）：
  - `libmsgpackc.so.2`
  - `libcudnn*.so*`
  - `libnccl*.so*`
  - `libcublas*.so*`
  - `libnvrtc*.so*`

### 4.4 执行通道差异

- `local_direct` 通道：所有库依赖必须在当前环境通过，不允许 defer
- `local_slurm` 通道：允许将计算节点特有的库检查推迟到 SLURM 作业执行阶段
- `ssh_*` 通道：远端检查按上述规则，登录节点/计算节点以远端环境为准

## 5. 通道级必检项

### 5.1 `local_direct`

- `runtime.script.work_dir` 存在；缺失时可退回到 `runtime.script.code_path` 所在目录
- 当前解释器可执行
- conda 环境可激活（若 `enabled=true`）
- `onescience`、`torch` 及业务依赖可导入
- `runtime.modules` 为空或可加载

### 5.2 `local_slurm`

- 除入口与环境检查外，确认当前环境可直接调用 `sbatch`、`squeue`、`sacct`
- `runtime.cluster.partition`、`nodes`、`cpus_per_task`、`time_limit` 等提交字段齐备
- 测试目录可写

### 5.3 `ssh_direct`

- `runtime.ssh.work_dir` 与 SSH 连接信息齐备
- 本地测试目录、入口脚本、远端工作目录和远端写入权限齐备
- readiness 检查必须通过 SSH / 远端通道确认，不得用本地 import 结果替代远端环境结论
- 不要求 SLURM 字段或 `sbatch` / `squeue` / `sacct` 可用

### 5.4 `ssh_slurm`

- `runtime.ssh.work_dir` 与 SSH 连接信息齐备
- 远端工作目录、入口脚本、SLURM 提交所需字段齐备
- readiness 检查必须通过 SSH / 远端通道确认，不得用本地 import 结果替代远端环境结论

### 5.5 `scnet_mcp`

- `runtime.scnet.*` 中的必要平台接入和提交信息齐备
- 本地测试目录、运行命令和提交清单存在
- `scnet.region`、`scnet.partition`/`scnet.queue`、`scnet.remote_work_dir`/`scnet.work_dir` 可用

## 6. 预检失败处理流程

### 6.1 失败分类

| 失败类型 | 判定条件 | 处理方式 |
|----------|----------|----------|
| Conda 配置缺失 | `runtime.conda` 缺失或结构无效 | 进入 conda 发现/安装流程 |
| 缺失 Python 包 | `ModuleNotFoundError` | 进入 `install_intent=python_packages` 安装流程 |
| 缺失 CUDA 扩展 | `ImportError` + CUDA 相关 | 进入源码编译安装流程 |
| 缺失数据文件 | 文件不存在 | 返回阻断，建议 orchestrator 插入下载/定位步骤 |
| 权限问题 | `PermissionError` / `Access denied` | 返回阻断，要求用户授权或调整 |
| GPU 不可用 | `torch.cuda.is_available()=False` | 确认是否需要 GPU；若需要则返回阻断 |
| 环境不一致 | `pip check` 返回冲突 | 进入 `pip install` 修复冲突 |
| GPU 显存不足（单卡） | 显存预算估算 > 95% 且任务不支持多 seed | 返回阻断并建议降低输入规模 |
| GPU 显存不足（全部卡） | 多卡聚合后 0 张卡可行 | 返回阻断，`blocking_reason=gpu_oom_all_gpus_insufficient` |
| GPU 显存高风险（多卡可行） | 多卡聚合后 >=2 张卡可行 | 返回 `partial` 状态，附带多 seed 并行建议 |

### 6.2 修复规则

1. 预检失败后，installer 先分析失败原因
2. 对于 installer 可自行修复的项（缺包、conda 配置），直接进入对应安装/修复分支
3. 修复完成后重新执行预检；预检通过后方可返回成功状态
4. 对于超出 installer 边界的问题（权限、数据文件、GPU 硬件不足），返回阻断状态并附带建议

### 6.3 不应阻塞的情况

以下情况不应判定为预检失败：
- SLURM 通道中登录节点缺失计算节点专属共享库（按 4.3 规则处理为 deferred）
- 预估显存使用 < 60% 但 `nvidia-smi` 显示有其他进程占用（记录 warning，不阻塞）

## 7. 输出契约

预检完成后返回结构化结果：

```yaml
preflight_result:
  status: passed | partial | failed | blocked
  checks:
    conda_config: passed | failed | skipped
    python_interpreter: passed | failed | skipped
    onescience_import: passed | failed | skipped
    torch_cuda: passed | failed | skipped
    business_dependencies:
      - name: <模块名>
        status: passed | failed
    entry_script: passed | failed | skipped
    environment_consistency: passed | failed | skipped
    gpu_accessible: passed | failed | skipped
    data_files: passed | failed | skipped
    gpu_memory_budget:
      estimated_total_gb: <数值>
      available_per_gpu_gb: <数值>
      risk_level: low | medium | high | exceeded
      recommendation: <建议文本>
  warnings: []
  missing_libs_on_login_node: []
  deferred_lib_checks: false
  blocking_reason: <仅 status=blocked 时>
  next_action: <修复建议或 continue>
  resume_target: <委托来源，如 onescience-runtime 或 onescience-orchestrator>
  resume_phase: <恢复阶段>
```

## 8. 硬门禁

- 预检验证阶段：可直接执行所有检测命令，不需要用户确认。
- 检测完成后只报告结果；若需进入安装/修复分支，仍需获得用户明确同意（遵循 installer 主流程的硬门禁规则）。
- `run_site=remote` 时，所有远端检测必须通过 SSH 执行，不得在本端 shell 执行远端环境的检测命令。
- 不得在预检阶段创建 conda 环境或安装任何包；如需修复，应切换到对应的安装分支。
- 检测失败不等于任务失败；installer 按 6.1 分类表决定是自行修复、返回 `failed` 还是 `blocked`。

## 9. 与主流程的关系

当 `installer_reason=preflight_validation` 时：
- 跳过 `discover-route.md` 中的意图识别（意图已知 = 预检验证）
- 跳过 bootstrap 和 python_packages 安装分支
- 直接进入本文件的预检流程
- 若预检发现环境缺失需要修复，再路由到对应安装分支
- 完成后按 `resume_target` 回到调用方
