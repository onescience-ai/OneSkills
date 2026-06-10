# Runtime Probe Contract

本文件定义 `onescience-runtime` 内部环境探测的最小契约。probe 是 `discover/preflight` 的内部能力，不是新的公开 skill。

## 一、目标

probe 负责把用户语义线索和候选目标，通过实际接入通道确认成可消费的环境事实。

它回答：

- 目标通道是否可访问
- 候选 Host / region / queue / path 是否真实可用
- 运行所需的调度器、解释器、module、conda、driver stack 是否 ready
- 探测结果能否归一化为 `hardware_profile`、`backend_id` 与 `execution_readiness`

probe 不回答：

- 是否应该安装依赖
- 是否应该修改用户配置
- 是否应该提交训练 / 推理作业
- 业务脚本是否正确

probe 中出现的 `module load`、`conda activate` 或轻量环境探针只表示进入目标运行上下文以确认 readiness，不表示 runtime 拥有安装职责。任何 `conda create`、`pip install`、工作区克隆或 shell 初始化修改都应交给 `onescience-installer`。

## 二、输入

probe 输入至少包含：

- `probe_channel`: `ssh_slurm` / `scnet_mcp` / `local`
- `semantic_environment_hints`: 用户语义中的候选线索
- `probe_target`: 已确认或待确认的 Host / region / queue / path
- `requested_checks`: 本轮需要确认的检查项

语义线索只能作为候选，不能直接升级为环境事实。

## 三、输出

probe 输出建议保持下面结构：

```json
{
  "example_id": "ssh_slurm_dcu_probe_success",
  "probe_channel": "ssh_slurm",
  "execution_mode": "remote_slurm",
  "access_mode": "ssh",
  "probe_status": "succeeded",
  "probe_target": {
    "host": "login-kunshan",
    "partition": "hpctest01"
  },
  "observed_environment_facts": {
    "scheduler_type": "slurm",
    "accelerator_kind": "dcu",
    "accelerator_vendor": "amd",
    "driver_ready": true,
    "torch_ready": true
  },
  "normalized_output": {
    "hardware_profile_ready": true,
    "expected_backend_id": "slurm_dcu",
    "execution_readiness": "ready_to_execute",
    "blocking_reason": "none"
  }
}
```

## 四、状态语义

`probe_status` 当前建议使用：

- `succeeded`
- `blocked`
- `partial`

`blocking_reason` 当前建议优先复用 runtime 既有原因；probe 专属原因可以先留在 probe example 中，不直接扩成全局 runtime result 枚举。

常见原因：

- `none`
- `ssh_connect_failed`
- `partition_not_accessible`
- `missing_sbatch`
- `python_not_ready`
- `torch_not_ready`
- `scnet_service_unavailable`
- `queue_not_accessible`
- `remote_path_not_writable`
- `probe_channel_not_confirmed`

## DCU 软件栈判定

DCU backend 的软件栈 readiness 不能只用 `python` 或 `torch import` 判断。DCU 运行依赖 DTK 用户态运行时，或依赖已经封装 DTK 的 `sghpc` 环境；因此 `slurm_dcu` / SCnet DAS 归一化前至少需要确认：

- 目标队列或远端 shell 已进入已确认的软件环境，例如 `sghpcdas/25.6` 与包含 DTK 的 `sghpc-mpi-gcc/26.3`。
- 若目标是 SCnet/DAS 或已显式设置 `ONE_PROBE_PRESERVE_CONDA_PYTHON=true`，必须先激活 conda 并保存 `PYTHON_BIN="${CONDA_PREFIX}/bin/python3"`，再加载 SGHPC/DAS module；probe 后续必须使用保存的解释器。
- `dtk_runtime_ready=true` 或 `sghpc_runtime_ready=true`，并可给出 `hipcc`、`LD_LIBRARY_PATH`、module load 结果等 evidence。
- `python_ready=true` 与 `torch_ready=true` 必须在上述软件环境加载之后检查；裸 `python3` 失败不能覆盖已加载 DTK / sghpc 后的事实。
- `python_bin`、`conda_prefix`、`saved_python_from_conda` 与 `torch_import_ok` 应进入 evidence，避免 module 改写 `PATH` 后选错解释器。
- 若 `torch_ready=true` 但 DTK / sghpc 用户态 runtime 未确认，不能把 DCU backend 标记为 `ready_to_execute`。

## 五、通道要求

### `ssh_slurm`

只允许只读或最小安全探测：

- SSH 连通性
- `sinfo` / `squeue` / `sbatch --version`
- partition 是否存在
- CPU / accelerator 可见性
- module / conda / python / torch 可用性
- 路径存在性与写权限

不要在 probe 阶段提交训练作业或安装依赖。

#### `ssh_slurm` 推荐探测顺序

`ssh_slurm` 通道探测按下面顺序推进。前一步失败时不要伪造后续事实，也不要把用户语义线索直接升级成 `hardware_profile`。

1. Host 确认：目标 Host 必须来自用户确认、项目配置或上游已确认上下文；多 Host 候选时返回 `probe_channel_not_confirmed`。
2. SSH 连通性：用非交互 SSH 连接确认 Host、认证、host key 与基本 shell 可用；失败返回 `ssh_connect_failed`。
3. SLURM CLI：确认 `sbatch --version`、`sinfo`、`squeue` 或等价命令可用；缺失返回 `missing_sbatch`。
4. partition / account：确认候选 partition 存在、当前用户可见；不可见或不可访问返回 `partition_not_accessible`。
5. 资源可见性：确认 CPU 架构、GPU/DCU 类型、设备数量、可见性环境变量与候选 backend 匹配。
6. 软件栈 readiness：先按已确认的 module / conda 规则进入目标软件环境，再确认 python / torch / 分布式运行时；解释器不可用返回 `python_not_ready`，torch 不可用返回 `torch_not_ready`。
7. 路径 readiness：确认远端工作目录存在或可创建、可写；不可写返回 `remote_path_not_writable`。
8. 归一化：只有 Host、SLURM、partition、资源、软件栈和路径均满足目标 runtime profile 时，才可输出 `execution_readiness=ready_to_execute`。

probe 阶段不检查业务脚本正确性，不提交 `sbatch` 作业，也不修改远端环境。需要用临时文件确认写权限时，应使用最小临时文件并清理；如果清理失败，仍要在 evidence 中说明。

可复用的远端信号采集模板位于 `../assets/probe_templates/ssh_slurm_probe.sh`。该模板只输出 key/value 事实信号，不直接生成最终 probe JSON；runtime 需要把这些信号归一化到本文件定义的 `observed_environment_facts` 与 `normalized_output`。

如果 SSH 已连到 SCnet / SLURM 登录节点，软件环境判断也必须遵循目标平台规则。以 SCnet DAS 为例，应通过 `ONE_PROBE_PRESERVE_CONDA_PYTHON=true` 先激活目标 conda 环境并保存 conda Python，再通过 `ONE_PROBE_MODULES="sghpcdas/25.6 sghpc-mpi-gcc/26.3"` 加载已确认 module，然后检查 `dtk_runtime_ready` / `sghpc_runtime_ready`、`python_ready`、`torch_ready` 与 DCU runtime；不要用未加载 module 的裸 `python3` 结果覆盖 DAS 环境事实，也不要在 module 加载后用 PATH 中的 DAS Python 代替目标 conda Python。非 SCnet/DAS 的通用 SSH/SLURM 环境不默认启用该解释器固定策略。

#### `ssh_slurm` 归一化边界

- DCU + AMD + `HIP_VISIBLE_DEVICES` + DTK / sghpc 用户态 runtime + RCCL readiness 可以归一化到 `slurm_dcu`。
- NVIDIA GPU + `CUDA_VISIBLE_DEVICES` + NCCL readiness 可以归一化到 `slurm_gpu` 或多机 GPU backend，但必须同时满足节点数与分布式 profile 要求。
- CPU-only SLURM 可以归一化到 `slurm_cpu`，不得因为缺 GPU/DCU 自动判为环境失败。
- `expected_backend_id` 可以是候选 backend，但只有实际探测证据足够时，`hardware_profile_ready` 才能为 `true`。

### `scnet_mcp`

通过 MCP 工具确认：

- 服务是否可调用
- region 是否可列出
- queue 是否可访问
- remote path 是否可写
- 目标队列内的软件环境是否 ready
- task_id 是否可查
- stdout / stderr 是否可下载

SCnet MCP 不可用是外部依赖阻断，不是 runtime 契约失败。

如果需要确认 SCnet DAS / torch 环境，不要用本地 Python 或未加载 DAS 的裸 `python3` 结果作为最终判断。runtime 应在目标队列中提交轻量环境 probe task，例如 `../assets/probe_templates/scnet_das_torch_probe.sh`，先固定目标 conda Python，再加载 `sghpcdas/25.6` 与包含 DTK 的 `sghpc-mpi-gcc/26.3`，再读取 `python_bin`、`conda_prefix`、`saved_python_from_conda`、`dtk_runtime_ready` / `sghpc_runtime_ready`、`python_ready`、`torch_import_ok`、`torch_ready` 与 `dcu_runtime_ready`。该 probe task 不属于训练 / 推理作业，必须保持最小化、可审计，并通过 `safety.submitted_job=false` 与 `safety.submitted_probe_task=true` 区分。

### `local`

`probe_channel=local` 需要区分两类 readiness：

- `execution_mode=local`：本地直跑 readiness
- `execution_mode=local_slurm`：本地 Slurm readiness

本地直跑只做本地只读检查或安全路径检查：

- Python 可用性
- 依赖 import
- 数据 / 模型 / 工作目录
- CPU / GPU 可见性

本地 Slurm 额外确认：

- `sbatch` / `squeue` / `sacct` 是否可直接调用
- 当前 partition / queue 是否可访问
- 本地渲染后的 job script 路径是否可写
- 目标 module / conda / python / torch 是否 ready

## 六、安全边界

- 不修改 `onescience.json`
- 不安装依赖
- 不提交训练 / 推理任务
- 不创建或修改 conda 环境
- 不克隆、更新或安装 OneScience 工作区
- 不把语义线索直接写成 `hardware_profile`
- 不伪造探测结果
- 探测失败时必须返回 `probe_status` 与 `blocking_reason`
