# SCnet Runtime Channel

本文件说明 `onescience-runtime` 在 `scnet_mcp` 通道下的路由条件、委托边界、结果归一化规则与常见错误解释。

这条链路表达为：

- `execution_mode=remote_direct`
- `access_mode=cloud_api`

`execution_channel=scnet_mcp` 用于标记这条 `remote_direct + cloud_api` 的 SCnet 云平台执行上下文；命中 SCnet 作业、文件、账户、区域、队列或集群相关需求时，直接调用 `scnet-chat` 技能执行。

## 通道前置条件

`scnet_mcp` 依赖本地可访问的 SCnet 平台接入能力，不是仓库内部自带能力。

进入该通道前至少确认：

- 当前机器仍安装了 SCnet 所需接入
- 当前会话还能正常访问 SCnet 平台
- 需要真实回归时，维护记录里要显式写明本次使用的本地环境可访问该服务

如果服务已卸载、未安装或连接不可用：

- 将状态标记为 `blocked`
- 允许继续完成静态契约、文档、路由与安装器校验
- 不要把这类失败归因为 runtime 逻辑回归，除非已证明确实能连通目标平台
- 结构化返回建议对齐 `skills/onescience-runtime/assets/examples/scnet_mcp_runtime_result_service_unavailable.json`

## 何时选择 `scnet_mcp` 对应的 `remote_direct`

满足以下任一条件时，runtime 应优先选择 `scnet_mcp`：

- 用户明确提到 `SCnet`
- 请求里直接出现区域、队列、`task_id`、下载日志、MCP 提交
- 目标是把本地最小脚本或现有脚本交给 SCnet 平台做真实执行验证

## 委托边界

当请求命中以下 SCnet 需求时，直接调用 `scnet-chat` 技能执行：

- 作业查询、历史作业、实时作业、作业详情
- 作业提交、删除作业、观察已有 `task_id`
- 文件列表、上传、下载、创建、删除、复制、移动、重命名
- 账户信息、余额、机时、作业统计
- 区域切换、队列查询、集群信息、缓存刷新

runtime 在 SCnet 通道中仍负责：

- 判断当前请求是否应进入 SCnet 路由
- 检查本地入口脚本、命令、提交文件清单是否完整
- 保持远程意图边界，不在本地执行业务脚本替代远程验证
- 将交接输入整理给 `scnet-chat`
- 消费 `scnet-chat` 返回的状态、日志、阻断与平台错误，并归一化为 runtime 输出

## 远程意图下的本地边界

如果用户明确要求远程执行、远程测试、提交到 SCnet 或提交到 SLURM，远程意图优先于本地最小验证建议：

- 不得本地执行测试脚本、训练脚本、业务入口脚本，或通过 import 运行依赖来判断远程环境。
- 本地只允许做 `local_preparation`：文件存在性检查、提交文件清单、命令模板渲染、提交脚本生成和不触发业务依赖的静态语法检查。
- 真正的运行验证必须通过目标远程通道完成；本地依赖缺失不得替代远程环境结论。
- 输出 evidence 时建议显式记录 `local_execution=skipped_by_remote_intent`。

只有在用户没有明确远程执行意图，且任务本身是“先生成代码再提交”的普通准备流程时，才可以在用户授权范围内做本地最小验证；该验证失败也不得覆盖远程通道探测结论。

## runtime 在委托前需要确认的最小事实

runtime 在把任务交给 `scnet-chat` 前，优先确认：

- 当前请求确实是 SCnet 目标任务
- 是“提交新任务”还是“观察已有任务”还是“平台管理类操作”
- 若提交任务：本地脚本路径、运行命令、提交文件清单是否存在
- 若观察已有任务：`task_id` 与 `region` 是否已提供，或是否需要由 `scnet-chat` 进一步解析
- 若需要环境安装或修复：回退到 `onescience-installer`，不要在 runtime 中补装

这些检查通过后，直接调用 `scnet-chat` 技能执行 SCnet 平台侧的区域解析、队列选择、任务状态读取、日志下载、文件管理与账户查询等动作。

## 路径、区域与队列规则

调用 `scnet-chat` 技能执行平台动作后，runtime 在解释结果时仍应遵守以下规则：

### 1. 不要默认在 `/` 下创建目录

若结果显示根目录创建受限，例如：

- `创建文件夹失败: Insufficient authority, prohibit operation`

应解释为目标路径不可写，而不是业务脚本失败；结构化阻断建议对齐 `skills/onescience-runtime/assets/examples/scnet_mcp_runtime_result_remote_path_not_writable.json`。

### 2. 区域文件系统相互隔离

上传、日志下载、远端文件列表都依赖区域。

解释要求：

- 提交时使用哪个 `region`，后续状态、日志、文件结果也应继续绑定该 `region`
- 不要把一个区域里的远端路径拿去另一个区域直接解释成可复用提交目标

### 3. 切区后不要复用旧队列

常见错误：

- 切到新区域后仍沿用旧区域默认队列
- 返回 `未找到可访问的队列`

runtime 在归一化结果时，应把它解释为区域/队列不匹配，并建议重新选择当前区域可访问队列；结构化阻断建议对齐 `skills/onescience-runtime/assets/examples/scnet_mcp_runtime_result_queue_not_accessible.json`。

## 软件环境 readiness

通用 probe 输出契约见 `./runtime_probe_contract.md`。本节只保留 `scnet_mcp` 通道下对结果解释仍有价值的约束。

### Probe 边界

如果需要判断 DAS / torch / DCU runtime readiness：

- 不要用本地 PATH 或裸 `python3` 结论代替队列内事实
- 只接受目标队列内轻量 probe task 返回的环境信号
- probe task 只采集环境信号，不运行用户业务脚本，不安装依赖，不修改配置
- 如果 `scnet-chat` 已覆盖该平台动作，runtime 只消费 probe 返回的证据，不再自定义调用顺序

### DAS / torch 环境解释规则

SCnet 新一代机器中，DCU 运行依赖 DTK 用户态 runtime，HPCSDK 集成环境 `sghpc-mpi-gcc/26.3` 包含 DTK；DAS / conda 环境需要通过 module 进入：

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

runtime 解释结果时应遵守：

- 如果 `python_bin` 不是目标 conda 环境里的解释器，优先判断为解释器选择错误
- 如果 `module load sghpcdas/25.6` 与 `module load sghpc-mpi-gcc/26.3` 后 `torch_ready=true` 且 DTK / sghpc runtime 已确认，不应再返回 `python3_not_found` 或 `torch_not_ready`
- 如果裸 `python3` 不存在，但 DAS probe 成功，应以 DAS probe 结果为准
- 如果需要 `conda create`、`pip install` 或环境修复，回退 `onescience-installer`

## 状态与日志判定

### 1. `completed` 只代表调度完成

任务状态 `completed` 后，仍然必须检查：

- 标准输出 `.out`
- 错误日志 `.err`

SCnet `completed` 只代表调度完成；没有业务 success marker 时，应视为验证未完成或失败，而不是仅凭状态判定成功。

### 2. 状态查询回退要保留来源

如果直接任务状态查询失效，而 `scnet-chat` 或平台侧回退到区域任务列表匹配当前 `task_id`：

- 不要伪装成主查询成功
- 继续记录真实来源，例如 `status_source=scnet_list_regions_tasks`
- diagnose 应保留 fallback 来源，避免误导后续维护者

### 3. 排队阶段日志可能尚未生成

如果任务仍在 `queued` / `starting` 阶段，而下载结果只是占位内容，例如：

- `{"code":"911020","data":null,"msg":"File does not exist"}`

应按以下方式归一化：

1. 不要把这个内容当成真实 `.out/.err`
2. 记录 `log_readiness=not_ready`
3. 保持 `sync_status=not_started` 或 `partial`
4. 等真实日志生成后再视为可消费日志

### 4. 本地日志才是下游 diagnose 的稳定输入

一旦日志已由平台动作返回并同步到本地，`onescience-runtime` 的 diagnose 阶段应消费本地日志，不再重新定义额外的 SCnet 平台工作流。

## 平台侧异常

### `Transport closed`

含义：

- 平台连接中断
- 不能据此直接判断远端任务提交失败或成功

runtime 处理方式：

1. 记录平台调用中断
2. 如果 `scnet-chat` 返回了已执行的重试或恢复结果，保留该证据
3. 如果连接未恢复，停止新增推断，只报告“当前无法继续向平台发起调用”

### `Service unavailable / not installed`

含义：

- 本机未安装 SCnet 所需接入
- 或该服务已被卸载，当前会话根本无法发起平台调用

runtime 处理方式：

1. 停止真实提交流程
2. 在结果中明确写出“环境阻断，不是作业结果”
3. 把剩余工作收束到文档、资产、静态 QA 和待恢复回归计划
4. 与 `Transport closed` 区分：
   - `Service unavailable` 表示服务根本不可调用，通常应返回 `submission_state=not_started`
   - `Transport closed` 表示会话中途断开，可返回 `submission_state=failed` 或 `not_started`
