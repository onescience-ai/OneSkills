# Diagnose

在 execute 结束后读取本文件，对执行结果做基础诊断与下一步路由。

## Inputs

- `execution_channel`
- `submission_target`
- `submission_state`
- `execution_state`
- `log_state`
- `job_id` 或 `task_id`
- `local_log_dir`
- `synced_logs`
- `sync_status`
- `evidence.execute`

## Stable Failure Classes

诊断阶段只收口到以下基础分类：

- `submission_failed`
- `slurm_resource_unavailable`
- `slurm_resource_retry_exhausted`
- `environment_not_ready`
- `logs_not_ready`
- `business_script_failed`
- `status_fallback_used`

## Diagnose Rules

1. 提交命令失败、`sbatch` 失败、平台提交失败、连接中断导致未完成提交时，优先归类为 `submission_failed`。
2. 缺解释器、缺包、conda 不可用、OneScience/torch 不可导入、分布式运行时未就绪时，归类为 `environment_not_ready`。
3. 任务仍在排队、日志占位文件尚未生成、同步未开始或仅拿到占位响应时，归类为 `logs_not_ready`。
4. 已有明确业务日志、退出码或错误输出指向用户脚本本身失败时，归类为 `business_script_failed`。
5. 若状态判定依赖 fallback 查询而不是主查询路径，保留 `status_fallback_used` 与真实 `status_source`。
6. 若 `execution_mode=slurm` 且证据指向 partition、GRES、`gpus_per_node`、memory、CPU、node 或 time limit 不可用，先归类为 `slurm_resource_unavailable`，读取 `./references/slurm-resource-retry.md` 并尝试受控调整；只有超过重试预算或无法安全调整时，才归类为 `slurm_resource_retry_exhausted`。

## Next Action Routing

- SLURM partition 或资源不可用且仍在重试预算内 -> `next_action=onescience-runtime`，读取 `./references/slurm-resource-retry.md` 后重新渲染并重试原测试任务
- SLURM 资源重试耗尽、找不到兼容 partition，或调整会改变用户明确要求的并行规模 -> `next_action=onescience-runsite` 或 `ask_user`，并带上 `candidate_partitions`、`adjusted_cluster_overrides`、`resource_probe_evidence`
- 环境/缺包/解释器问题 -> `next_action=onescience-installer`，并立即调用 `skills/onescience-installer/SKILL.md`；无需向用户二次确认。installer verify 成功后回到 `preflight`，重新通过后继续执行原测试任务。
- `work_dir`、入口路径、module 名称、不可自动调整的 cluster 资源字段或执行三元组存在配置问题 -> `next_action=onescience-runsite`，并立即调用 `skills/onescience-runsite/SKILL.md`；无需向用户二次确认。runsite 成功补齐或确认配置后回到 `discover`，重新通过后继续执行原测试任务。
- 已有明确业务日志、退出码或错误输出指向用户脚本本身失败 -> `next_action=onescience-coder` 或回上游 skill
- 仅日志未就绪、任务仍在运行或等待 -> `next_action=onescience-runtime`

## Rules

- diagnose 只消费已拿到的执行证据，不重新安装环境，也不修改代码。
- 一旦日志已同步到本地，应以本地日志作为稳定诊断输入。
- 日志未就绪不能直接归因为业务脚本失败。
- 远程意图任务仍然保持远程边界，不用本地执行业务脚本补证据。
- `next_action=onescience-runsite` 或 `next_action=onescience-installer` 是自动技能交接，不是用户确认提示。
- 自动交接成功解除阻断后，不要以“配置/环境已修复”结束；必须恢复 runtime 阶段并继续原测试任务，直到拿到执行/诊断结果或新的阻断。
- 对 SLURM 资源反馈，优先消费 `evidence.execute.slurm_adjustments`；如果已经调整成功，不要再把原始 partition/memory 错误报告成最终失败。

## Output

diagnose 至少产出：

- `failure_reason`
- `status_source`
- `log_readiness`
- `next_action`
- `evidence.diagnose`
- `slurm_resource_adjusted`
- `adjusted_cluster_overrides`
- `retry_count`

若已有执行证据，建议继续输出：

- `job_id` 或 `task_id`
- `local_log_dir`
- `synced_logs`
- `sync_status`
