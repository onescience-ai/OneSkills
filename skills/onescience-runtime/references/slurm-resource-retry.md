# SLURM Resource Retry

当 `execution_mode=slurm` 且 `execution_channel` 为 `local_slurm` 或 `ssh_slurm` 时读取本文件。本文件只处理 SLURM 调度层反馈出的 partition 与资源不可用问题。

## Trigger Signals

从以下证据中识别可重试资源问题：

- `sbatch` stderr：invalid partition、partition not found、Requested node configuration is not available、invalid generic resource、Invalid GRES、Memory specification can not be satisfied、QOS/association resource limit。
- `squeue` / `sacct` reason：PartitionConfig、ReqNodeNotAvail、Resources、QOSMaxGRES、QOSMaxMemory、AssocMaxGRES、AssocMaxMem、BadConstraints、OUT_OF_MEMORY。
- 作业日志：oom-kill、Out Of Memory、CUDA/DCU device count less than requested、GRES unavailable。

不要把 Python ImportError、业务脚本异常、数据文件缺失或模型错误归入本流程。

## Probe Commands

本地 SLURM 直接执行；远程 SSH SLURM 必须通过目标 SSH host 执行，不能用本地集群信息替代远端。

优先使用：

```bash
sinfo -h -o "%P|%a|%D|%c|%m|%G|%l"
scontrol show partition
scontrol show nodes
sacctmgr show qos format=Name,MaxTRESPU,MaxTRESPerUser,MaxWall -P
```

如果 `sacctmgr` 不可用，不要阻断；只基于 `sinfo`、`scontrol` 和错误反馈继续判断。

## Adjustment Rules

只做临时执行覆盖，不直接写回 `onescience.json`。把覆盖值记录到 `evidence.execute.slurm_adjustments`：

- `original_cluster`
- `adjusted_cluster`
- `feedback_signal`
- `probe_commands`
- `candidate_partitions`
- `retry_count`

### Partition

当反馈表明 partition 不存在、不可用或当前 partition 不接受请求资源时：

1. 用 `sinfo/scontrol` 列出 `up` 或可提交的 partition。
2. 优先选择与原始 `runtime.target.accelerator_kind`、`runtime.cluster.gpu_type`、`nodes`、`gpus_per_node`、`cpus_per_task`、`memory` 兼容的 partition。
3. 若多个 partition 兼容，优先选择默认 partition（`*`）、空闲资源更多、时间限制满足请求的候选。
4. 只替换 `cluster.partition` 并重渲染 `run_job.slurm`；其它字段保持不变。

找不到兼容 partition 时，不要猜测；转 `next_action=onescience-runsite`，并带上探测到的 partition 列表和失败原因。

### GPU / GRES

当反馈表明 `gpus_per_node` 或 `gpu_type/GRES` 不可用时：

1. 解析 `sinfo/scontrol` 中的 GRES，例如 `gpu:4`、`gpu:a100:8`、`dcu:4`。
2. 优先切换到支持原始 `gpu_type` 的 partition。
3. 如果同一 partition 最大 GPU 数小于请求值，且业务入口没有显式要求固定 GPU 数，可以把 `gpus_per_node` 降到可用最大值，并同步重渲染 torchrun 的 `--nproc_per_node`。
4. 如果用户或上游 handoff 明确要求固定 GPU 数、多机并行规模或固定 device count，不要自动降低 GPU 数；转 `next_action=onescience-runsite` 或请求用户确认。

### Memory

当反馈表明内存请求无法满足时：

1. 对 `runtime.cluster.memory` 和 `sinfo/scontrol` 的内存单位做归一化，统一比较 MB/G/GB。
2. 若提交阶段提示请求内存超过 partition/node 上限，优先寻找满足原请求的其它 partition；没有时可把 `memory` 降到候选 partition 的最大可用值。
3. 若作业已运行后因 OOM 失败，允许把 `memory` 增加到下一档或 partition 最大值后重试一次；不要把 OOM 误判为业务脚本失败。
4. 如果调整后的内存低于用户明确要求，或 OOM 后没有更高可用内存，停止并报告资源阻断。

### CPU / Nodes / Time

当反馈明确指出 `nodes`、`cpus_per_task`、`ntasks_per_node` 或 `time_limit` 超出 partition/QOS 限制时：

- 优先选择能满足原请求的 partition。
- 若只能降低资源，必须确认不会改变用户明确要求的并行规模；否则停止并报告阻断。
- 不要自动增加节点数、GPU 数或运行时长，除非反馈给出明确的最小需求且该增加不会提高用户未授权的资源级别。

## Retry Budget

- 对提交前的 scheduler rejection，最多自动调整并重试 2 次。
- 对运行后 OOM，只允许自动增加 memory 并重试 1 次。
- 每次重试前必须重新生成并保留新的 `run_job.slurm`，不要原地无记录覆盖证据。
- 超过预算后停止，输出 `blocking_reason=slurm_resource_retry_exhausted`。

## Output Additions

进入本流程后，execute / diagnose 输出增加：

- `slurm_resource_adjusted=true|false`
- `adjusted_cluster_overrides`
- `retry_count`
- `retry_reason`
- `candidate_partitions`
- `resource_probe_evidence`

如果最终调整成功并完成提交或运行，最终答复要说明使用了哪些临时资源覆盖，并建议后续由 `onescience-runsite` 持久化配置；runtime 本身不写回 `onescience.json`。
