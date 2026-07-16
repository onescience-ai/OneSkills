---
name: onescience-runtime
description: 【统一运行与基础诊断技能】按 discover、preflight、execute、diagnose 固定闭环执行测试任务，依据 onescience.json 的 execution_profile 三元组路由执行通道；SCnet 提交任务时必须读取根级 onescience.json.scnet 并把 region、partition/queue、work_dir 和资源参数交给 scnet-chat；配置问题自动委托 onescience-runsite 补齐后回到 runtime 继续原测试任务，环境问题自动委托 onescience-installer 安装或修复并 verify 成功后回到 runtime 继续原测试任务；当 execution_mode 为 slurm 且提交或运行反馈表明 partition、gpus_per_node、memory 等资源不可用时，探测可用 SLURM 资源并受控调整后重试。
type: executor
---

# OneScience Runtime

## 执行流程

每次任务固定按 `discover -> preflight -> execute -> diagnose` 顺序处理。

### 1. discover

先读取项目根目录 `onescience.json`，优先消费：

- `runtime.execution_profile.run_site`
- `runtime.execution_profile.execution_mode`
- `runtime.execution_profile.access_mode`

`execution_channel` 由这三个字段派生；当前约定是 `run_site=local` 时 `access_mode` 允许为空，`execution_mode` 为空/`none` 视为非调度直接执行。若配置中已有 `execution_channel`，只作为对照证据，不作为唯一 routing 来源。

需要进入 discover 细节时，读取：

- `./references/discover.md`

### 2. preflight

discover 得到通道后，继续读取 `runtime.conda`：

- `runtime.conda.enabled`
- `runtime.conda.env_name`（仅 `enabled=true` 时需要）
- `runtime.conda.activate_script`（仅 `enabled=true` 时需要）

并按需读取：

- `runtime.scnet.*`（当 `execution_channel=scnet_mcp` 或后续需要委托 `scnet-chat` 提交任务时，这是 SCnet region/partition/work_dir/资源参数的唯一主来源）
- `runtime.modules.*`
- `runtime.script.work_dir`
- `runtime.script.*`
- `runtime.cluster.*`
- `runtime.target.*`
- `runtime.env_vars.*`
- `runtime.ssh.work_dir`
- `runtime.ssh.*`
- `runtime.scnet.work_dir`

需要进入预检细节时，读取：

- `./references/preflight.md`
- `./references/contract.md`

### 3. execute

preflight 确认可执行后，根据 `execution_channel` 只读取一个执行分支；只有 `runtime.conda.enabled=true` 时才会在对应模板中渲染 `activate_script`：

- `local_direct` -> `./references/execute-local-direct.md`
- `local_slurm` -> `./references/execute-local-slurm.md`
- `ssh_direct` -> `./references/execute-ssh-direct.md`
- `ssh_slurm` -> `./references/execute-ssh-slurm.md`
- `scnet_mcp` -> `./references/execute-scnet-skill.md`

若 `execution_mode=slurm` 且 `sbatch`、`squeue`、`sacct` 或作业日志反馈 partition / GRES / GPU 数 / memory / CPU / node 资源不可用，继续读取：

- `./references/slurm-resource-retry.md`

渲染脚本模板时只使用最小模板资产：

- `./assets/templates/local_direct.sh`
- `./assets/templates/slurm_cpu.sh`
- `./assets/templates/slurm_dcu.sh`
- `./assets/templates/slurm_gpu.sh`
- `./assets/templates/slurm_gpu_multinode_torchrun.sh`
- `./assets/tpl.slurm`

### 4. diagnose

执行结束后，基于状态、日志与错误证据进入基础诊断。

需要进入诊断细节时，读取：

- `./references/diagnose.md`

不要把所有执行分支一次性读入上下文；只继续当前命中的通道文件。

## Resume Invariant

`onescience-runsite` 和 `onescience-installer` 是 runtime 的中途修复步骤，不是最终任务终点。

- 调用 `onescience-runsite` 解决配置问题后，必须重新读取 `onescience.json`，从 `discover` 恢复，并继续执行原测试任务直到进入 `execute/diagnose` 或遇到新的真实阻断。
- 调用 `onescience-installer` 解决环境问题且 verify 成功后，必须重新读取 `onescience.json` 与 `runtime.conda`，从 `preflight` 恢复，并继续执行原测试任务直到进入 `execute/diagnose` 或遇到新的真实阻断。
- 不要把 `next_action=onescience-runsite` 或 `next_action=onescience-installer` 的一次性交接结果当作最终答复；只有对方阻断、需要用户补充信息、verify 失败，或恢复后出现新的阻断时，才停止并向用户报告。
- 恢复时沿用原始用户意图、测试入口、运行通道候选和已确认的远程边界；不要因修复完成而替换成新的本地最小验证。

## Hard Gates

- runtime 自身不要直接改写用户的 `onescience.json`；需要创建、补齐或修正运行站点配置时，必须立即加载并执行 `skills/onescience-runsite/SKILL.md`，由 `onescience-runsite` 按其边界写回或补问。
- `onescience.json` 缺失、三元组无法归一或关键字段冲突时，设置 `next_action=onescience-runsite` 作为内部交接标记，并直接调用 `onescience-runsite` 补齐配置；无需向用户二次确认，也不要自行猜测后继续执行。`onescience-runsite` 完成后，重新读取 `onescience.json` 并从 `discover` 恢复，继续原测试任务。
- 远程执行意图优先于任何本地最小验证建议。只要用户明确要求远程执行、提交到 SLURM 或提交到 SCnet，就不要在本地执行业务脚本替代远程验证。
- 发现 conda 缺失、conda 不可用、解释器缺失、缺包、OneScience/torch 不可导入或分布式运行时未就绪时，设置 `next_action=onescience-installer` 作为内部交接标记，并直接调用 `skills/onescience-installer/SKILL.md` 安装或修复；无需向用户二次确认，也不要在 runtime 中补装。installer verify 成功后，重新读取 `onescience.json` 和 `runtime.conda`，从 `preflight` 恢复，继续原测试任务。
- 命中 SCnet 作业、文件、账户、区域、队列、集群、日志下载等平台动作时，继续委托 `scnet-chat` 技能执行；runtime 只负责交接输入、消费结果与基础诊断。
- 通过 `scnet-chat` 提交任务前，必须先读取 `onescience.json.runtime.scnet` 中的 `region`、`partition`/`queue`、`remote_work_dir`/`work_dir`、资源参数和作业名等信息；`partition` 归一为 scnet-chat 的 `--queue` 参数。不要依赖 scnet-chat 的缓存默认区域或默认队列，也不要用用户自然语言里的 region/partition 直接覆盖该配置。
- 不要在代码入口、探针脚本或远端提交目标缺失时继续提交空作业。

## Output Contract

阶段汇报和最终输出至少包含：

- `execution_channel`
- `execution_mode`
- `access_mode`
- `submission_state`
- `execution_state`
- `log_state`
- `blocking_reason`
- `next_action`

若进入执行阶段，建议继续输出：

- `config_source`
- `region`
- `partition` 或 `queue`
- `submission_target`
- `job_id` 或 `task_id`
- `local_log_dir`
- `synced_logs`
- `sync_status`
- `status_source`
- `log_readiness`

若 `execution_mode=slurm` 且进入资源反馈调整流程，继续输出：

- `slurm_resource_adjusted`
- `adjusted_cluster_overrides`
- `retry_count`
- `retry_reason`
- `candidate_partitions`
