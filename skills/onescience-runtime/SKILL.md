---
name: onescience-runtime
description: 【统一运行与基础诊断技能】按 discover、preflight、execute、diagnose 固定闭环执行测试任务，依据 onescience.json 的 execution_profile 三元组路由执行通道；SCnet 提交任务时必须读取根级 onescience.json.scnet 并把 region、partition/queue、work_dir 和资源参数交给 scnet-chat；配置问题自动委托 onescience-runsite 补齐后回到 runtime 继续原测试任务，环境问题自动委托 onescience-installer 安装或修复并 verify 成功后回到 runtime 继续原测试任务；当 execution_mode 为 slurm 且提交或运行反馈表明 partition、gpus_per_node、memory 等资源不可用时，探测可用 SLURM 资源并受控调整后重试。
type: executor
---

# OneScience Runtime

## 执行流程

每次任务固定按 `discover -> preflight -> execute -> diagnose` 顺序处理。`execute` 是硬门禁阶段：只有 `preflight` 明确产出 `preflight_passed=true`、`execution_readiness=ready` 且 `evidence.preflight.status=passed` 后，才能读取和执行任何 execute 分支。缺少这些证据时，必须回到 `preflight`，不得直接提交本地、SSH、SLURM 或 SCnet 任务。

### 1. discover

先读取项目根目录 `onescience.json`，并立即调用 `skills/onescience-runsite/SKILL.md` 对当前运行站点配置做校验、复用或补齐；不要直接信任已有 `onescience.json`。只有 `onescience-runsite` 完成已有配置检查、远程连接验证或缺失字段补齐并写回后，runtime 才重新读取 `onescience.json`，再优先消费：

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

`runtime.conda` 缺失不是可默认跳过 conda 的信号。缺少该结构、`enabled` 缺失、`enabled=true` 但缺少 `env_name`，或无法通过当前执行通道确认环境 ready 时，必须设置 `next_action=onescience-installer` 并立即调用 `skills/onescience-installer/SKILL.md` 做发现、安装或修复；installer verify 成功后重新读取 `onescience.json` 与 `runtime.conda`，再从 `preflight` 重新检查。

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

preflight 确认可执行后，根据 `execution_channel` 只读取一个执行分支；只有 `runtime.conda.enabled=true` 时才会在对应模板中渲染 `activate_script`。

进入 execute 前必须重新核对：

- `preflight_passed=true`
- `execution_readiness=ready`
- `blocking_reason` 为空或 `none`
- `evidence.preflight.status=passed`
- `evidence.preflight.conda_checked=true`
- `evidence.preflight.environment_checked=true`

任一缺失或为 false 时，禁止读取 execute 分支，必须回到 `preflight`。若阻断原因是缺少 `runtime.conda`、conda 不可用、解释器缺失、缺包、OneScience/torch 不可导入或分布式运行时未就绪，立即委托 `onescience-installer`，不要自行假设环境可用。

execute 分支映射：

- `local_direct` -> `./references/execute-local-direct.md`
- `local_slurm` -> `./references/execute-local-slurm.md`
- `ssh_direct` -> `./references/execute-ssh-direct.md`
- `ssh_slurm` -> `./references/execute-ssh-slurm.md`
- `scnet_mcp` -> `./references/execute-scnet-skill.md`

### 进度监控与超时策略

对于预估执行时间 > 10 分钟的任务，应采用分段式执行策略，避免单次长超时后进度完全丢失：

1. **分段超时**：将单次长超时（如 3600000ms）拆分为多段较短的超时（如每段 600000ms），每段结束后检查中间产物：
   - 检查日志文件是否有新的输出行（对比行数变化）
   - 检查预期输出目录是否出现新的中间文件
   - 若连续 2 段无任何进度变化，判定为卡死，触发 diagnose

2. **中间产物检查点**：
   - 批量任务应在每个批次完成后写入中间状态文件（如 `checkpoint_batch_<N>.json`），记录已完成的数据项索引
   - 超时恢复时，通过中间状态文件判断已完成进度，仅处理剩余任务，避免全部重来
   - 参考案例：大批量序列推理被超时中断，若有进度文件则可在超时后从断点续跑

3. **默认并行化引导**：
   - 当任务涉及 N > 100 个独立数据项且按任务目标可并行处理时，runtime 应在 execute 前检查可用 GPU 数量并输出并行化建议
   - 建议格式：`本任务涉及 {N} 个独立数据项，当前可用 {G} 个 GPU，建议拆分为 {S} 个分片并行执行`

### 日志落盘策略

进入 execute 阶段后，先解析当前测试目录 `work_dir`：优先取 `runtime.script.work_dir`，缺失时回退到 `runtime.script.code_path` 所在目录。所有执行通道的本地日志目录统一为 `<work_dir>/logs/`，`local_log_dir` 必须输出该路径；不要再把远程任务日志下载到项目根目录 `.onescience/logs/<job_name>/`。

- `local_direct` / `local_slurm`：在测试目录内创建 `logs/`，stdout/stderr、`*.out`、`*.err` 均写入或复制到该目录。
- `ssh_direct` / `ssh_slurm`：远端上传目录为 `<runtime.ssh.work_dir>/<测试目录名>/`，远端日志目录为该目录下的 `logs/`；任务结束后用 `rsync/scp` 同步到本地 `<work_dir>/logs/`。
- `scnet_mcp`：交接给 `scnet-chat` 时显式要求平台日志下载到当前测试目录的 `logs/`，并在 runtime 输出中记录 `local_log_dir=<work_dir>/logs/`。
- `job_name` 只用于作业名、日志文件名前缀或远端任务识别；不再作为本地日志目录的额外子目录。

> `<work_dir>/logs/` 下的日志与 runtime 声明的输出文件，只有在 preflight 通过并进入真实 `execute` 阶段后，才可作为权威训练 / 推理 / 评测运行证据。runtime 不得为了满足 expected outputs 而创建占位或合成的 `trainer.log`、`train.log`、`metrics.json`、`predictions.json`、`targets.json` 等证据文件；若在 `execute` 前被阻断，应输出结构化状态、阻断原因和缺失产物信息，而不是补造运行结果。

若 `execution_mode=slurm` 且 `sbatch`、`squeue`、`sacct` 或作业日志反馈 partition / GRES / GPU 数 / memory / CPU / node 资源不可用，继续读取：

- `./references/slurm-resource-retry.md`

渲染脚本模板时只使用最小模板资产，并按执行通道与目标硬件做确定映射：

- `local_direct` -> `./assets/templates/local_direct.sh`
- `ssh_direct` -> `./assets/templates/local_direct.sh`
- `local_slurm` 且目标硬件为 CPU -> `./assets/templates/slurm_cpu.sh`
- `ssh_slurm` 且目标硬件为 CPU -> `./assets/templates/slurm_cpu.sh`
- `local_slurm` 且目标硬件为 DCU -> `./assets/templates/slurm_dcu.sh`
- `ssh_slurm` 且目标硬件为 DCU -> `./assets/templates/slurm_dcu.sh`
- `local_slurm` 且目标硬件为 GPU -> `./assets/templates/slurm_gpu.sh`
- `ssh_slurm` 且目标硬件为 GPU -> `./assets/templates/slurm_gpu.sh`
- 仅当预检已确认多机多卡 torchrun 入口与所需字段齐备时，SLURM 分支才允许改用 `./assets/templates/slurm_gpu_multinode_torchrun.sh`
- `./assets/tpl.slurm` 只作为兼容兜底参考，不作为 `local_slurm` / `ssh_slurm` 的默认模板选择结果

### 4. diagnose

执行结束后，基于状态、日志与错误证据进入基础诊断。

需要进入诊断细节时，读取：

- `./references/diagnose.md`

不要把所有执行分支一次性读入上下文；只继续当前命中的通道文件。

## Resume Invariant

`onescience-runsite` 和 `onescience-installer` 是 runtime 的中途修复步骤，不是最终任务终点。

- runtime 允许自动委托的下游技能仅限 `onescience-runsite`、`onescience-installer`，以及文档中已明确的平台动作执行方 `scnet-chat`；这些委托只用于恢复当前 runtime 步骤，不决定新的业务 executor。
- 调用 `onescience-runsite` 解决配置问题后，重新读取 `onescience.json`，从 `discover` 恢复，并继续原测试任务直到进入 `execute/diagnose` 或遇到新的真实阻断。
- 调用 `onescience-installer` 解决环境问题且 verify 成功后，重新读取 `onescience.json` 与 `runtime.conda`，从 `preflight` 恢复，并继续原测试任务直到进入 `execute/diagnose` 或遇到新的真实阻断。
- `next_action=onescience-runsite` 或 `next_action=onescience-installer` 只是一次性内部交接；只有对方阻断、需要用户补充信息、verify 失败，或恢复后出现新的阻断时，才停止并向用户报告。
- 恢复时沿用原始用户意图、测试入口、运行通道候选和已确认的远程边界；不要因修复完成而替换成新的本地最小验证。
- 若 diagnose 或执行证据表明后续问题已超出 runtime 的运行治理边界（例如需要新的业务代码实现、训练/推理策略重定义、后续评估阶段选择等），runtime 只返回 `execution_result` 中的 observation / recommendation，由 `onescience-orchestrator` 决定下一技能；runtime 不自行切换到 `onescience-coder`、`onescience-trainer`、`onescience-infer` 等业务 executor。

## Hard Gates

- runtime 自身不要直接改写用户的 `onescience.json`；discover 每次进入时都必须立即加载并执行 `skills/onescience-runsite/SKILL.md` 做运行站点校验。已有配置时先让 runsite 走检查/复用/远程连接验证分支，缺失或冲突时再由 runsite 按其边界写回或补问。
- `onescience-runsite` 完成校验、确认可复用或补齐配置后，runtime 必须重新读取 `onescience.json` 并从 `discover` 继续；不要直接使用 runsite 调用前缓存的三元组或历史 `execution_channel`。
- `onescience.json` 缺失、三元组无法归一或关键字段冲突时，设置 `next_action=onescience-runsite` 作为内部交接标记，并直接调用 `onescience-runsite` 补齐配置；无需向用户二次确认，也不要自行猜测后继续执行。`onescience-runsite` 完成后，重新读取 `onescience.json` 并从 `discover` 恢复，继续原测试任务。
- 远程执行意图优先于任何本地最小验证建议。只要用户明确要求远程执行、提交到 SLURM 或提交到 SCnet，就不要在本地执行业务脚本替代远程验证。
- 未完成 preflight 或 preflight 未通过时，禁止进入 execute。不得因为已有 `execution_channel`、已有脚本路径、用户说“跑一下”或存在历史 `onescience.json` 就跳过环境发现检查。
- 发现 conda 缺失、conda 不可用、解释器缺失、缺包、OneScience/torch 不可导入或分布式运行时未就绪时，设置 `next_action=onescience-installer` 作为内部交接标记，并直接调用 `skills/onescience-installer/SKILL.md` 安装或修复；无需向用户二次确认，也不要在 runtime 中补装。installer verify 成功后，重新读取 `onescience.json` 和 `runtime.conda`，从 `preflight` 恢复，继续原测试任务。
- 命中 SCnet 作业、文件、账户、区域、队列、集群、日志下载等平台动作时，继续委托 `scnet-chat` 技能执行；runtime 只负责交接输入、消费结果与基础诊断。
- 通过 `scnet-chat` 提交任务前，必须先读取 `onescience.json.runtime.scnet` 中的 `region`、`partition`/`queue`、`remote_work_dir`/`work_dir`、资源参数和作业名等信息；`partition` 归一为 scnet-chat 的 `--queue` 参数。不要依赖 scnet-chat 的缓存默认区域或默认队列，也不要用用户自然语言里的 region/partition 直接覆盖该配置。
- 不要在代码入口、探针脚本或远端提交目标缺失时继续提交空作业。

## Output Contract

阶段汇报和最终输出至少包含：

- `execution_channel`
- `execution_mode`
- `access_mode`
- `preflight_passed`
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
