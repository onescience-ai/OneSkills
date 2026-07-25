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
