# Runtime Contract

本文件用于说明 `onescience-hardware`、`onescience-coder`、`onescience-runtime` 三层之间的交接关系，以及统一运行入口下各执行通道的职责归属。

## 当前 runtime 稳定后端

当前仓库在 `ssh_slurm` 通道上稳定支持的后端是：

- `backend_id: slurm_dcu`
- `backend_id: slurm_gpu`

具体链路边界以 `skills/onescience-runtime/assets/backend_specs.json` 中的 `support_matrix` 为准。

## 先后顺序

远程运行类任务默认按下面顺序推进：

1. `onescience-hardware`
2. `onescience-coder`
3. `onescience-runtime`
4. `onescience-debug`（按需）

不要把 `onescience-runtime` 当成硬件探测层，也不要让 `onescience-hardware` 直接承担运行提交主职责。
对于显式 `SCnet` 请求，也仍然进入 `onescience-runtime`，但选择 `execution_channel=scnet_mcp`。

## 三层职责

### `onescience-hardware`

负责回答“运行环境是什么”：

- 用哪个 Host
- CPU 架构、厂商与节点拓扑是什么
- 加速卡类型、厂商、数量与设备可见性变量是什么
- 可用队列或分区是什么
- 需要哪些 module / conda 约束
- 数据、模型、工作目录的远端约定是什么
- 这个环境支持哪类运行后端与启动方式

### `onescience-coder`

负责回答“代码要怎么写”：

- 数据读取入口
- 模型与组件实现
- 训练 / 推理入口脚本
- 基于交接摘要实现设备、路径、批大小、分布式方式相关的适配点

它不负责连接远程环境，也不负责提交作业，也不直接参与硬件探测。

### `onescience-runtime`

负责回答“代码怎么跑起来”：

- 先选择 `execution_channel`
- 在 `ssh_slurm` 通道里读取 `onescience.json`、模板和完整硬件画像，生成并提交作业
- 在 `scnet_mcp` 通道里通过本地 SCnet MCP 上传脚本、提交任务、查状态并下载日志
- 统一产出作业状态、本地日志路径和下一步动作给 `onescience-debug`
- 在同一工作流内维护远程提交业务授权状态

## 字段分层

### 1. 环境事实

这些字段只能来自 `onescience-hardware` 输出的完整硬件画像，并仅在 `ssh_slurm` 通道里作为必选输入：

- `host`
- `scheduler_type`
- `platform_type`
- `partition`
- `cpu.*`
- `accelerators[]`
- `software.modules`
- `software.conda_env`
- `storage.dataset_dir`
- `storage.models_dir`
- `storage.work_dir`
- `capabilities.*`

### 2. `ssh_slurm` 任务申请

这些字段主要来自项目级 `onescience.json` 或用户任务输入：

- `runtime.cluster.nodes`
- `runtime.cluster.gpus_per_node`
- `runtime.cluster.cpus_per_task`
- `runtime.cluster.time_limit`
- `runtime.cluster.memory`
- `runtime.script.code_path`
- `runtime.script.job_name`

### 3. 通道选择字段

这些字段由 `onescience-runtime` 自身维护：

- `execution_channel`
- `submission_target`
- `job_status`
- `sync_status`

其中：

- `submission_target` 在 `ssh_slurm` 中通常表现为 `host/partition`
- `submission_target` 在 `scnet_mcp` 中通常表现为 `region/queue`

### 4. `ssh_slurm` 渲染与提交字段

这些字段由 `onescience-runtime` 在选定 backend 后补齐：

- `runtime.script.path`
- `runtime.script.generate`
- `runtime.script.template`
- `backend_id`
- 模板变量映射结果

### 5. `scnet_mcp` 通道字段

这些字段主要来自用户请求、上游上下文或 runtime 在 SCnet 提交时补齐：

- `region`
- `queue`
- `local_input`
- `remote_path`
- `command`
- `task_id`
- `observations.status_source`
- `observations.log_readiness`

这些字段不要求写入 `onescience.json`。

## `ssh_slurm` 通道里的 `onescience.json` 字段归属

### 主要由 `onescience-hardware` 感知后校准

- `runtime.cluster.partition`
- `runtime.cluster.gpu_type`
- `runtime.modules`
- `runtime.conda.env_name`
- `runtime.script.env_vars.ONESCIENCE_DATASETS_DIR`
- `runtime.script.env_vars.ONESCIENCE_MODELS_DIR`

### 主要由 `onescience-coder` 决定

- `runtime.script.code_path`
- `runtime.script.job_name`

### 主要由 `onescience-runtime` 决定或补齐

- `runtime.script.path`
- `runtime.script.generate`
- `runtime.script.template`
- `runtime.logs.remote_dir`
- `runtime.logs.local_dir`
- `runtime.logs.include_patterns`
- `runtime.logs.wait_for_completion`
- `runtime.logs.sync_after_completion`
- `runtime.submission.confirm_before_first_submit`
- `runtime.submission.reuse_confirmation_in_workflow`

缺失日志字段时，`ssh_slurm` 通道使用保守默认值：远端 `logs`，本地 `.onescience/logs`，同步 `*.out` / `*.err`，作业完成后自动同步。
缺失提交授权字段时，runtime 使用保守默认值：如果用户已经明确要求远程运行，则视为当前工作流已授权；否则第一次真正提交前可确认一次，同一工作流后续提交、轮询、日志同步和同配置重试复用该确认。

### 需要用户或任务共同决定

- `runtime.cluster.nodes`
- `runtime.cluster.gpus_per_node`
- `runtime.cluster.cpus_per_task`
- `runtime.cluster.time_limit`
- `runtime.cluster.memory`

这些是资源申请策略，不应只靠某一层单独猜测。

## CPU 与加速卡组合

不要把 CPU 仅仅视作 `cpus_per_task`，也不要把加速卡仅仅视作 `gpu_type`。

真实环境往往是：

- `AMD CPU + AMD DCU`
- `Intel CPU + NVIDIA GPU`
- `x86 CPU only`
- `ARM CPU + NVIDIA GPU`

这些组合会影响：

- 设备可见性变量
- 分布式后端
- 模板选择
- dataloader / 线程设置
- 环境初始化方式

因此：

- CPU / accelerator 组合属于 `hardware facts`
- 资源申请数量属于 `job request`
- 模板渲染与提交属于 `runtime backend`

## Runtime Backend 选择

当前 `ssh_slurm` 通道的 runtime backend 选择应以 `backend_specs.json` 的 selector 为准。

典型映射如下：

| scheduler_type | accelerator_kind | accelerator_vendor | backend_id |
| --- | --- | --- | --- |
| `slurm` | `dcu` | `amd` | `slurm_dcu` |
| `slurm` | `gpu` | `nvidia` | `slurm_gpu` |
| `slurm` | `cpu` | `none` | `slurm_cpu` |

## Backend Registry

当前 `ssh_slurm` 通道的 runtime backend registry 位于：

- `skills/onescience-runtime/assets/backend_specs.json`

消费时重点关注：

- `selector`
- `support_matrix`
- `template`
- `render_fields`

其中：

- `selector` 负责说明这个 backend 适用于哪类硬件画像
- `support_matrix` 负责表达 runtime / installer / debug 三条链路的支持边界
- `render_fields` 负责说明 runtime 在渲染模板前必须准备哪些字段

## `slurm_dcu` 渲染字段

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

这里的 `backend.*` 字段不应由用户手写在 `onescience.json` 中，而应由 `onescience-runtime` 根据 backend 规则与完整硬件画像渲染。
