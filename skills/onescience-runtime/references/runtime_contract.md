# Runtime Contract

本文定义 `onescience-runtime` 的字段归属、后端选择、模板渲染规则和作业提交流程。

## 稳定后端

当前 `ssh_slurm` 通道稳定支持的后端：
- `backend_id: slurm_dcu`
- `backend_id: slurm_gpu`

具体链路边界以 `assets/backend_specs.json` 的 `support_matrix` 为准。

## 典型执行顺序

远程运行类任务默认按以下顺序推进：

1. `onescience-coder`
2. `onescience-runtime`
3. `onescience-debug`（按需）

对于显式 SCnet 请求，也进入 `onescience-runtime`，但选择 `execution_channel=scnet_mcp`。

## 职责边界

### `onescience-runtime`

负责回答"代码怎么跑起来"：

- **自行完成远端主机发现与硬件探测**（不自其他技能获取硬件画像）
- 选择 `execution_channel`（`ssh_slurm` / `scnet_mcp`）
- 在 `ssh_slurm` 通道里读取 `onescience.json`、模板和探测结果，渲染并提交作业
- 在 `scnet_mcp` 通道里通过 SCnet MCP 工具上传脚本、提交任务、查状态并下载日志
- 统一产出作业状态、本地日志路径和下一步动作
- 维护远程提交的授权状态

### `onescience-coder`

负责回答"代码要怎么写"：

- 数据读取入口
- 模型与组件实现
- 训练 / 推理入口脚本

它不负责连接远程环境，也不负责提交作业。

## 环境事实

**环境事实由 runtime 自主远端探测获取**，包括：

- `host` — SSH 目标地址
- `scheduler_type` — 调度器类型（如 `slurm`）
- `platform_type` — 平台类型（如 `cluster`）
- `accelerator_kind` — 加速器类型（`dcu` / `gpu` / `cpu`）
- `accelerator_vendor` — 厂商（`amd` / `nvidia` / `none`）
- `partition` — 队列/分区（从 `onescience.json` 读取）
- `modules` — 可用模块（从 `onescience.json` 或远端探测）
- `conda_env` — conda 环境（从 `onescience.json` 读取）

## 字段分层

### 1. 集群配置（来自 `onescience.json`）

- `runtime.cluster.partition`
- `runtime.cluster.gpu_type`
- `runtime.cluster.nodes`
- `runtime.cluster.gpus_per_node`
- `runtime.cluster.cpus_per_task`
- `runtime.cluster.time_limit`
- `runtime.cluster.memory`
- `runtime.modules`
- `runtime.conda.env_name`
- `runtime.script.env_vars.ONESCIENCE_DATASETS_DIR`
- `runtime.script.env_vars.ONESCIENCE_MODELS_DIR`

其中 `nodes`、`gpus_per_node`、`cpus_per_task`、`time_limit`、`memory` 属资源申请策略，需要用户确认。

### 2. 代码配置（来自 coder 输出）

- `runtime.script.code_path`
- `runtime.script.job_name`

### 3. 通道选择与运行时状态（runtime 自身维护）

- `execution_channel`
- `submission_target`
- `job_status`
- `sync_status`

其中：

- `submission_target` 在 `ssh_slurm` 中为 `host/partition`
- `submission_target` 在 `scnet_mcp` 中为 `region/queue`

### 4. 渲染与提报字段（runtime 在选中 backend 后补齐）

- `runtime.script.path`
- `runtime.script.generate`
- `runtime.script.template`
- `backend_id`
- 模板变量映射结果
- `backend.module_setup`（从 backend_specs.json 读取）
- `backend.device_visibility_export`（从 backend_specs.json 读取）

### 5. 日志字段（runtime 补齐，支持默认值）

- `runtime.logs.remote_dir` — 默认 `logs`
- `runtime.logs.local_dir` — 默认 `.onescience/logs`
- `runtime.logs.include_patterns` — 默认 `*.out` / `*.err`
- `runtime.logs.wait_for_completion` — 默认 `true`
- `runtime.logs.sync_after_completion` — 默认 `true`

### 6. 提交授权字段（runtime 维护）

- `runtime.submission.confirm_before_first_submit` — 默认 `true`
- `runtime.submission.reuse_confirmation_in_workflow` — 默认 `true`

默认行为：第一次提交前确认一次，同一工作流后续提交复用该确认。

### 7. `scnet_mcp` 通道字段

- `region`
- `queue`
- `local_input`
- `remote_path`
- `command`
- `task_id`
- `observations.status_source`
- `observations.log_readiness`

不要求写入 `onescience.json`。

## CPU 与加速卡组合

不要把 CPU 仅视作 `cpus_per_task`，也不要把加速卡仅视作 `gpu_type`。

真实环境组合：

- `AMD CPU + AMD DCU`
- `Intel CPU + NVIDIA GPU`
- `x86 CPU only`
- `ARM CPU + NVIDIA GPU`

这些组合影响：

- 设备可见性变量
- 分布式后端
- 模板选择
- dataloader / 线程设置
- 环境初始化方式

分类：
- **CPU / accelerator 组合** → 由 runtime 远端探测确认
- **资源申请数量** → 来自 `onescience.json` / 用户任务输入
- **模板渲染与提交** → 属于 runtime backend 职责

## Runtime Backend 选择

当前 `ssh_slurm` 通道的 backend 选择以 `backend_specs.json` 的 selector 为准。

典型映射：

| scheduler_type | accelerator_kind | accelerator_vendor | backend_id |
|---|---|---|---|
| `slurm` | `dcu` | `amd` | `slurm_dcu` |
| `slurm` | `gpu` | `nvidia` | `slurm_gpu` |
| `slurm` | `cpu` | `none` | `slurm_cpu` |

### Backend Registry

位于 `assets/backend_specs.json`，消费时重点关注：

- `selector` — 依据远端探测结果匹配对应 backend
- `support_matrix` — runtime / installer / debug 三条链路的支持边界
- `template` — 模板文件名
- `render_fields` — 渲染前必须准备的字段清单

## `slurm_dcu` 模板渲染字段

当前 `slurm_dcu` 模板至少应能渲染以下字段：

- `cluster.partition`
- `cluster.nodes`
- `cluster.gpu_type`
- `cluster.gpus_per_node`
- `cluster.cpus_per_task`
- `cluster.ntasks_per_node`
- `cluster.time_limit`
- `cluster.memory`
- `script.job_name`
- `script.code_path`
- `conda.env_name`
- `env_vars.ONESCIENCE_DATASETS_DIR`
- `env_vars.ONESCIENCE_MODELS_DIR`
- `backend.module_setup`
- `backend.device_visibility_export`

`backend.*` 字段不由用户手写，而由 runtime 根据 backend 规则与探测结果渲染。
