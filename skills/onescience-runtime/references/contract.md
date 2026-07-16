# Contract

本文件说明 `onescience-runtime` 的共享输入输出、执行通道归一规则，以及自动委托 `onescience-runsite` / `onescience-installer` 时的统一交接结构。

## 固定阶段

`onescience-runtime` 对内固定拆成 4 个阶段：

1. `discover`
2. `preflight`
3. `execute`
4. `diagnose`

阶段顺序固定，不建议跳过前置阶段直接执行。

## 委托恢复不变量

`onescience-runsite` 与 `onescience-installer` 只负责解除 runtime 当前遇到的配置或环境阻断；它们成功后必须把控制权交回 `onescience-runtime`，由 runtime 继续原测试任务。

- 配置修复成功：重新读取根目录 `onescience.json`，从 `discover` 重新开始，并继续走 `preflight -> execute -> diagnose`。
- 环境修复且 installer verify 成功：重新读取根目录 `onescience.json` 与 `runtime.conda`，从 `preflight` 重新开始，并继续走 `execute -> diagnose`。
- 自动委托的 `next_action` 是内部交接标记，不是最终答复；不要在 runsite/installer 成功后停止在“已修复配置/环境”。
- 只有委托方被阻断、需要用户补充信息、installer verify 失败，或恢复后出现新的配置/环境/业务阻断时，才停止并报告当前阻断。
- 恢复后必须沿用原始测试意图、入口脚本、远程/本地边界和提交目标候选，不要把远程测试任务降级成本地 smoke test。

## 共享 phase context

建议在四阶段之间稳定传递以下字段：

- `run_site`
- `execution_mode`
- `access_mode`
- `execution_channel`
- `submission_target`
- `execution_readiness`
- `blocking_reason`
- `submission_state`
- `execution_state`
- `log_state`
- `evidence`

其中：

- `run_site/execution_mode/access_mode/execution_channel` 解决“走哪条链路”
- `submission_target` 解决“往哪里执行”
- `execution_readiness/blocking_reason` 解决“当前能不能继续”
- `submission_state/execution_state/log_state` 解决“现在跑到哪一步”

## 执行三元组与通道归一

规范字段：

- `run_site`: `local | remote`
- `execution_mode`: `slurm | empty_or_none`
- `access_mode`: `ssh | scnet | empty_for_local`

标准映射：

- `(local, none, empty)` -> `local_direct`
- `(local, slurm, empty)` -> `local_slurm`
- `(remote, none, ssh)` -> `ssh_direct`
- `(remote, slurm, ssh)` -> `ssh_slurm`
- `(remote, none, scnet)` -> `scnet_mcp`
- `(remote, slurm, scnet)` -> `scnet_mcp`，表示通过 SCnet 平台提交带队列/资源参数的任务，不在 runtime 中直接执行 `sbatch`

兼容归一仅在 discover 使用：

- `execution_mode=slurm` 表示调度执行
- `execution_mode` 为空、`none`、`None` 或 `null` 时，视为非调度直接执行
- `access_mode=scnet` 表示 SCnet 平台接入
- `access_mode=ssh` 表示 SSH 接入
- `run_site=local` 且 `access_mode` 为空、缺失、`none`、`None` 或 `null` 时，视为本地访问路径
- `enabled=false` 时，脚本不应激活 conda；`enabled=true` 时才允许使用 `activate_script`
- 若读到旧写法，只归一到上述三元组语义，不让旧字段反向驱动 routing

若归一后仍无法映射到上述 5 条通道，则：

- `next_action=onescience-runsite`
- `blocking_reason=unsupported_execution_tuple` 或 `config_tuple_conflict`
- 立即加载并执行 `skills/onescience-runsite/SKILL.md` 补齐配置；无需向用户二次确认。
- runsite 成功补齐或确认配置后重新读取根目录 `onescience.json`，从 `discover` 恢复，并继续原测试任务。

## 共享输入分层

### 1. 项目配置

优先来自根目录 `onescience.json`：

- `runtime.execution_profile.*`
- `runtime.conda.*`
- `runtime.scnet.*`（SCnet 提交任务的 region、partition/queue、work_dir 与资源参数主来源）
- `runtime.modules.*`
- `runtime.script.work_dir`
- `runtime.script.*`
- `runtime.cluster.*`
- `runtime.target.*`
- `runtime.env_vars.*`
- `runtime.ssh.work_dir`
- `runtime.ssh.*`
- `runtime.scnet.work_dir`

`runtime.conda` 只有两种有效形态：

- `{"runtime": {"conda": {"enabled": false}}}`
- `{"runtime": {"conda": {"enabled": true, "env_name": "...", "activate_script": "..."}}}`

只有 `enabled=true` 时，执行模板才会渲染 conda 激活步骤；`enabled=false` 时必须跳过激活步骤，直接以当前目标环境做 readiness 检查。

`runtime.modules` 的值按顺序逐个执行 `module load <module>`。

### SCnet 提交配置

凡是通过 `scnet-chat` 提交任务的工作流，runtime2 必须先读取 `onescience.json.runtime.scnet`，并把下列字段归一后交给 `scnet-chat`：

- `region`：SCnet 区域；必须显式传入或先切换到该区域，不依赖缓存默认区域。
- `partition`：OneScience 规范字段；提交给 scnet-chat 时映射为 `queue` / `--queue`。`queue` 只作为兼容别名。
- `remote_work_dir` 或 `work_dir`：映射为 `--work-dir`。
- `nodes`/`nnode`、`ppn`/`cpus_per_task`、`gpus_per_node`、`dcus_per_node`、`memory`/`job_mem`、`time_limit`/`wall_time`、`job_name`：按 scnet-chat 的显式参数透传。

禁止把 `runtime.cluster.partition` 当成 SCnet `partition` 的默认值；SSH/SLURM 集群配置和 SCnet 平台提交配置必须分开。若 `runtime.scnet` 中缺少提交必需字段，应自动委托 `onescience-runsite` 补齐，而不是让 `scnet-chat` 自行选择默认队列。

### 2. 语义环境线索

用户自然语言中的 Host、队列、区域、设备类型、module、conda 或远端路径只表示候选事实。未经过当前通道确认前，不要把这些线索直接升级为最终提交目标或环境已 ready 结论。

### 3. 执行证据

建议对内按阶段保留：

- `evidence.discovery`
- `evidence.preflight`
- `evidence.execute`
- `evidence.diagnose`

当 `execution_mode=slurm` 进入资源调整流程时，`evidence.execute` 还应保留：

- `slurm_adjustments.original_cluster`
- `slurm_adjustments.adjusted_cluster`
- `slurm_adjustments.feedback_signal`
- `slurm_adjustments.probe_commands`
- `slurm_adjustments.candidate_partitions`
- `slurm_adjustments.retry_count`

## Runsite handoff contract

当 discover、preflight、execute 或 diagnose 发现配置问题时，统一自动交给 `onescience-runsite`，交接结构至少包含：

- `next_action=onescience-runsite`
- `config_reason`
  - `missing_runtime_config`
  - `unsupported_execution_tuple`
  - `config_tuple_conflict`
  - `missing_work_dir`
  - `wrong_script_path`
  - `wrong_module_name`
  - `wrong_cluster_config`
  - `missing_scnet_submit_config`
  - `slurm_resource_retry_exhausted`
  - `slurm_resource_adjustment_requires_confirmation`
- `resume_target=onescience-runtime`
- `resume_phase=discover`
- `execution_context`
- `evidence`

调用规则：

1. 立即加载并执行 `skills/onescience-runsite/SKILL.md`；不要向用户二次确认是否委托。
2. runtime 自身不直接改写 `onescience.json`；由 runsite 按其规则创建、补齐、复用或补问。
3. runsite 成功补齐或确认配置后，runtime 必须重新读取根目录 `onescience.json`，从 `discover` 重新开始，并继续原测试任务；不得把 runsite 的成功交接作为最终输出。
4. runsite 若需要用户补充字段、远程连接验证失败或无法写回配置，runtime 才停止并报告阻断。

## Installer handoff contract

当 preflight 或 execute 发现环境问题时，统一自动交给 `onescience-installer`，交接结构至少包含：

- `next_action=onescience-installer`
- `installer_reason`
  - `missing_conda_config`
  - `conda_unusable`
  - `python_not_ready`
  - `onescience_not_ready`
  - `missing_packages`
  - `distributed_runtime_not_ready`
- `config_problem`
  - `missing_work_dir`
  - `wrong_script_path`
  - `wrong_module_name`
  - `wrong_cluster_config`
- `resume_target=onescience-runtime`
- `resume_phase=preflight`
- `execution_context`
  - `run_site`
  - `execution_mode`
  - `access_mode`
  - `execution_channel`
- `transport_context`
  - `runtime.ssh.work_dir` / `runtime.scnet.work_dir` 或等价字段
- `evidence`
  - conda 检查结果
  - import/probe 失败结果
  - 缺包或解释器错误信号

恢复规则：

1. 立即加载并执行 `skills/onescience-installer/SKILL.md`；不要向用户二次确认是否委托。
2. `onescience-installer` 完成环境修复并 verify 成功后，runtime 必须重新读取 `onescience.json.runtime.conda`。
3. 恢复点固定从 `preflight` 重新开始，不继续使用旧的内存态 conda 信息。
4. 重新通过 preflight 后，runtime 必须继续进入 `execute` 并运行原测试任务；不得把 installer 的成功 verify 作为最终输出。
5. runtime 不负责写回安装成功状态，只消费修复后最新的 `onescience.json`。
6. installer 若 verify 失败、安装被阻断或需要用户授权/补充信息，runtime 才停止并报告阻断。

## 稳定输出

runtime 对外至少稳定输出：

- `execution_channel`
- `execution_mode`
- `access_mode`
- `submission_state`
- `execution_state`
- `log_state`
- `blocking_reason`
- `next_action`

若进入执行与诊断链，建议同时输出：

- `submission_target`
- `job_id` 或 `task_id`
- `local_log_dir`
- `synced_logs`
- `sync_status`
- `status_source`
- `log_readiness`
- `slurm_resource_adjusted`
- `adjusted_cluster_overrides`
- `retry_count`

一句话原则：

`onescience-runtime` 负责“发现执行链路、做预检、执行、回收日志并给出基础诊断”；配置补齐自动交给 `onescience-runsite`，环境安装与修复自动交给 `onescience-installer`。
