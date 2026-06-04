# SCnet Runtime Channel

本文件定义 `onescience-runtime` 在 `scnet_mcp` 通道下的提交流程、路径约束与错误对照。

这条链路表达为：

- `execution_mode=remote_direct`
- `access_mode=cloud_api`

`execution_channel=scnet_mcp` 用于标记这条 `remote_direct + cloud_api` 运行链路。

## 通道前置条件

`scnet_mcp` 是依赖本地 SCnet MCP 服务的外部执行通道，不是仓库内部自带能力。

进入该通道前至少确认：

- 当前机器仍安装了 SCnet MCP
- 当前会话还能正常调用 SCnet MCP 接口
- 需要真实回归时，维护记录里要显式写明本次使用的本地环境可访问该服务

如果服务已卸载、未安装或连接不可用：

- 将状态标记为 `blocked`
- 允许继续完成静态契约、文档、路由与安装器校验
- 不要把这类失败归因为 runtime 逻辑回归，除非已证明确实能连通 MCP
- 结构化返回建议对齐 `skills/onescience-runtime/assets/examples/scnet_mcp_runtime_result_service_unavailable.json`

## 何时选择 `scnet_mcp` 对应的 `remote_direct`

满足以下任一条件时，runtime 应优先选择 `scnet_mcp`：

- 用户明确提到 `SCnet`
- 请求里直接出现区域、队列、`task_id`、下载日志、MCP 提交
- 目标是把本地最小脚本或现有脚本直接上传到 SCnet 做真实执行验证

## 最小闭环

1. `scnet_list_regions`
2. `scnet_get_resources(region=...)`，或直接使用 `scnet_list_regions` 返回的队列
3. `scnet_upload_file(local_path=..., region=...)`
4. `scnet_submit_task(region=..., queue=..., command=...)`
5. `scnet_get_task_status(task_id=..., region=...)`
6. `scnet_download_log(task_id=..., region=..., log_type=stdout/stderr)`

## 远程意图下的本地边界

如果用户明确要求远程执行、远程测试、提交到 SCnet 或提交到 SLURM，远程意图优先于本地最小验证建议：

- 不得本地执行测试脚本、训练脚本、业务入口脚本，或通过 import 运行依赖来判断远程环境。
- 本地只允许做 `local_preparation`：文件存在性检查、提交文件清单、命令模板渲染、提交脚本生成和不触发业务依赖的静态语法检查。
- 真正的运行验证必须通过目标远程通道完成；本地依赖缺失不得替代远程环境结论。
- 输出 evidence 时建议显式记录 `local_execution=skipped_by_remote_intent`。

只有在用户没有明确远程执行意图，且任务本身是“先生成代码再提交”的普通准备流程时，才可以在用户授权范围内做本地最小验证；该验证失败也不得覆盖远程通道探测结论。

如果 `scnet_get_task_status` 已不能稳定返回旧任务或已完成任务状态：

7. 回退到 `scnet_list_regions_tasks(region=...)`
8. 通过 `task_id` 匹配当前任务，再解释 `statQ / statR / statC`

## 目录与权限规则

### 1. 不要默认在 `/` 下创建目录

实测里，直接在根目录创建文件夹可能返回：

- `创建文件夹失败: Insufficient authority, prohibit operation`

默认策略：

- 优先直接上传到用户家目录或家目录下已存在的可写目录
- 若确实需要目录，先用 `list_files` 或 `file_exists` 判断家目录下的目标目录是否可写
- 需要临时目录时，优先在家目录下选择已存在或可写的位置；`./tmp` 只作为明确验证可写后的兜底选择
- 如果 `create_folder` 返回 `Insufficient authority, prohibit operation`，不要继续重试根目录建目录
- 若确认当前目标路径不可写，结构化阻断返回建议对齐 `skills/onescience-runtime/assets/examples/scnet_mcp_runtime_result_remote_path_not_writable.json`

### 2. 区域文件系统相互隔离

上传、日志下载、远端文件列表都依赖区域。

执行要求：

- 上传脚本用哪个 `region`，提交任务、查状态、下载日志就继续用哪个 `region`
- 不要把一个区域里的远端路径拿去另一个区域直接提交

## 队列选择规则

### 1. 先看该区域真实可用队列

不要依赖本地环境里的历史默认值。即使用户没给 `queue`，也先从：

- `scnet_list_regions`
- `scnet_get_resources(region=...)`

读取当前区域可访问队列，再显式提交。

### 2. 切区后不要复用旧队列

常见错误：

- 切到新区域后仍沿用旧区域默认队列
- 返回 `未找到可访问的队列`

修复动作：

- 显式传 `queue`
- 该 `queue` 必须来自当前 `region` 的返回结果
- 结构化阻断返回建议对齐 `skills/onescience-runtime/assets/examples/scnet_mcp_runtime_result_queue_not_accessible.json`

### 3. `account/partition` 组合错误通常不是脚本问题

常见错误：

- `Batch job submission failed: Invalid account or account/partition combination specified`

修复动作：

- 更换当前区域下另一个有权限的队列
- 或改到另一个用户确实有权限的区域
- 不要在脚本内容上浪费时间

## 运行环境探测

通用 probe 输出契约见 `./runtime_probe_contract.md`。本节只补充 `scnet_mcp` 通道的具体探测动作。

### Probe 顺序

`scnet_mcp` 通道探测按下面顺序推进，前一步失败时不要伪造后续事实：

1. 服务可调用性：调用轻量 MCP 接口确认本地服务仍可用。
2. 区域可访问性：读取授权区域列表，确认目标 `region` 存在。
3. 队列可访问性：读取目标区域资源或队列，确认目标 `queue` 属于当前区域且当前用户可访问。
4. 远端路径可写性：优先检查用户家目录或已存在目标目录；必要时使用最小临时文件或上传探针确认写权限。
5. 软件环境 readiness：如果要判断 DAS / torch / DCU runtime，必须在目标队列内运行轻量环境探针，不要用本地 PATH 或裸 `python3` 结论代替队列内事实；DCU 必须同时确认 DTK 用户态 runtime 或封装它的 `sghpc` 环境。
6. 已有任务观察：若输入已有 `task_id`，先查 `scnet_get_task_status`；失败时回退到 `scnet_list_regions_tasks`。
7. 日志 readiness：下载 stdout / stderr 后检查是否是真实日志；占位 JSON 只能标记为 `not_ready`。

probe 阶段不提交训练 / 推理作业；但在 SCnet MCP 通道中，软件环境 readiness 只能通过目标队列内的轻量 probe task 确认。该 probe task 必须只采集环境信号，不运行用户业务脚本，不安装依赖，不修改配置。只有用户明确要求执行，且 `preflight` 已确认目标、队列和路径后，才进入正式 `execute`。

### DAS / torch 环境探测

SCnet 新一代机器手册说明，DCU 运行依赖 DTK 用户态 runtime，HPCSDK 集成环境 `sghpc-mpi-gcc/26.3` 包含 DTK；DAS / conda 环境需要通过 module 进入：

```bash
module use /work2/share/sghpc_sdk/modulefiles/
module load sghpc-mpi-gcc/26.3
module load sghpcdas/25.6
```

因此不要把下面结论直接当成 torch 不可用：

```bash
python3 -c 'import torch'
```

如果目标环境同时包含用户 conda 环境和 SGHPC/DAS module，解释器选择顺序必须固定：

1. 先 source `/etc/profile` 与用户 shell 初始化文件。
2. 激活目标 conda 环境，例如 `onescience311`。
3. 保存 `PYTHON_BIN="${CONDA_PREFIX}/bin/python3"`。
4. 再加载 `sghpc-mpi-gcc/26.3` 与 `sghpcdas/25.6`。
5. 用保存的 `${PYTHON_BIN}` 做 torch / DTK probe，不要在 module 加载后重新用 `command -v python3` 选择解释器。

原因是 module 加载可能改写 `PATH`，把解释器切到 DAS Python；这会导致 `ModuleNotFoundError: No module named 'torch'`，但真实问题不是用户 conda 环境没有 torch，而是 probe 选错了解释器。

正确策略：

1. 先确认 MCP、region、queue、remote path。
2. 上传 `skills/onescience-runtime/assets/probe_templates/scnet_das_torch_probe.sh` 或等价最小脚本。
3. 通过 `scnet_submit_task` 在目标 `region` / `queue` 中运行：

```bash
bash scnet_das_torch_probe.sh
```

4. 下载 stdout / stderr，读取 `das_module_loaded`、`hpcsdk_module_loaded`、`conda_prefix`、`python_bin`、`saved_python_from_conda`、`dtk_runtime_ready`、`sghpc_runtime_ready`、`python_ready`、`torch_import_ok`、`torch_ready`、`dcu_runtime_ready` 等 key/value 信号。
5. 只有该轻量 probe task 在队列内确认 DTK / sghpc 用户态 runtime 与 `torch_ready=true` 后，才把 DAS torch 环境标记为 ready。

如果 `module load sghpcdas/25.6` 与 `module load sghpc-mpi-gcc/26.3` 后 `torch_ready=true` 且 DTK / sghpc runtime 已确认，runtime 不应再返回 `python3_not_found` 或 `torch_not_ready`。如果裸 `python3` 不存在，但 DAS probe 成功，应以 DAS probe 结果为准。

某些队列里不保证 `python3` 在 `PATH`。

如果解释器不确定，先提交轻量探针；对于 DAS / torch 场景，优先使用上面的 DAS probe，而不是只执行裸解释器探测：

```bash
which python3 || which python || ls -1 /usr/bin/python* /usr/local/bin/python* 2>/dev/null || echo NO_PYTHON_FOUND
```

如果需要进一步判断 module，可再补一条只读探针：

```bash
module avail 2>/dev/null || echo NO_MODULE_CMD
```

## 状态与日志判定

### 1. `completed` 只代表调度完成

任务状态 `completed` 后，仍然必须检查：

- 标准输出 `.out`
- 错误日志 `.err`

### 环境失败模式

常见 SCnet / DAS 环境失败应先按环境证据分类，不要直接归因到业务代码：

- `ModuleNotFoundError: No module named 'torch'`：如果 `python_bin` 不是目标 conda 环境里的解释器，优先判断为解释器选择错误；应先保存 conda Python，再加载 SGHPC/DAS module。
- `ImportError: libgalaxyhip.so.5: cannot open shared object file`：通常表示 conda Python 有 torch，但 DTK / HIP 用户态 runtime 没进入 `LD_LIBRARY_PATH`；应确认 `sghpc-mpi-gcc/26.3` 与 `sghpcdas/25.6` 已加载。
- SCnet `completed` 只代表调度完成；没有业务 success marker 时，应视为验证未完成或失败，而不是仅凭状态判定成功。

典型场景：

- 调度成功
- 业务脚本失败
- `.err` 里出现 `python3: command not found`

### 2. `scnet_get_task_status` 失败时要回退

实测里，已完成任务后续再查时，可能出现：

- `error_code: 404`
- `message: 获取任务状态失败: 'NoneType' object has no attribute 'get'`

处理方式：

1. 不要直接把它判成任务不存在
2. 继续调用 `scnet_list_regions_tasks(region=...)`
3. 用 `task_id` 在该区域任务列表中匹配状态
4. 把最终状态来源记录为 `status_source=scnet_list_regions_tasks`

### 3. 排队阶段日志可能尚未生成

实测里，任务仍在 `queued` / `starting` 阶段时，下载日志可能得到一个“下载成功但文件内容是占位 JSON”的本地文件，例如：

- `{"code":"911020","data":null,"msg":"File does not exist"}`

处理方式：

1. 不要把这个内容当成真实 `.out/.err`
2. 记录 `log_readiness=not_ready`
3. 保持 `sync_status=not_started` 或 `partial`
4. 继续轮询任务状态，等日志真正生成后再下载

### 4. 本地日志才是下游 diagnose 的稳定输入

下载日志后，直接在 `onescience-runtime` 的 diagnose 阶段消费本地日志，不再依赖额外 skill。

## MCP 侧异常

### `Transport closed`

含义：

- MCP 连接中断
- 不能据此直接判断远端任务提交失败或成功

处理方式：

1. 先重试一个轻量接口，例如 `scnet_list_regions` 或 `scnet_interaction_manual`
2. 如果连接恢复，再继续提交或查状态
3. 如果连接未恢复，停止新增推断，只报告“当前无法继续向平台发起调用”

### `Service unavailable / not installed`

含义：

- 本机未安装 SCnet MCP
- 或该服务已被卸载，当前会话根本无法发起 MCP 调用

处理方式：

1. 停止真实提交流程
2. 在结果中明确写出“环境阻断，不是作业结果”
3. 把剩余工作收束到文档、资产、静态 QA 和待恢复回归计划
4. 与 `Transport closed` 区分：
   - `Service unavailable` 表示服务根本不可调用，通常应返回 `submission_state=not_started`
   - `Transport closed` 表示会话中途断开，可返回 `submission_state=failed` 或 `not_started`
