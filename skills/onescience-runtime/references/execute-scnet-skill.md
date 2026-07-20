# Execute SCnet Skill

当 `execution_channel=scnet_mcp` 时读取本文件。

## Inputs

- `execution_channel=scnet_mcp`
- `submission_target`
- `onescience.json.runtime.conda`
- `onescience.json.runtime.scnet`
- `runtime.modules.*`
- `runtime.script.work_dir`
- `runtime.script.code_path`
- `runtime.script.job_name`
- `runtime.scnet.work_dir`
- `runtime.cluster.*`
- `runtime.target.*`
- `runtime.env_vars.*`
- `evidence.preflight`
- 用户当前意图：提交新任务 / 观察已有任务 / 平台管理动作

## Entry Gate

进入本执行分支前必须已有当前轮次 preflight 证据：`preflight_passed=true`、`execution_readiness=ready`、`evidence.preflight.status=passed`、`evidence.preflight.conda_checked=true`、`evidence.preflight.environment_checked=true`、`evidence.preflight.channel_checked=true`、`evidence.preflight.entrypoint_checked=true`。任一缺失或失败时，不得委托 `scnet-chat` 提交新任务，必须回到 `preflight`；若缺少 `runtime.conda` 或目标环境未 ready，立即委托 `onescience-installer`。

## Routing Boundary

`scnet_skill` 表示 `run_site=remote + access_mode=scnet` 的 SCnet 平台执行上下文；`execution_mode` 可以为空、`none` 或 `slurm`。当 `execution_mode=slurm` 时，runtime2 仍然委托 `scnet-chat` 提交任务，只把队列和资源字段整理为 scnet-chat 参数，不在本地或远端直接执行 `sbatch`。

命中以下平台动作时，继续直接委托 `scnet-chat`：

- 作业提交、查询、删除、观察已有 `task_id`
- 文件列表、上传、下载、创建、删除、复制、移动、重命名
- 账户信息、余额、机时、作业统计
- 区域切换、队列查询、集群信息、缓存刷新
- 平台侧日志下载

runtime 在本通道中只负责：

- 判断是否应进入 SCnet 路由
- 准备要上传的测试文件、`run_job.slurm`、运行命令和目标目录
- 整理交接输入给 `scnet-chat`
- 消费 `scnet-chat` 返回的状态、日志、阻断与平台错误
- 把结果归一化为 runtime 输出

## SCnet Config Handoff

凡是通过 `scnet-chat` 提交新任务，必须先读取 `onescience.json.runtime.scnet` 并构造结构化交接。不要让 `scnet-chat` 根据缓存默认区域、默认队列或自然语言猜测提交目标。

必需字段：

- `scnet.region`
- `scnet.partition` 或兼容别名 `scnet.queue`
- `scnet.remote_work_dir` 或兼容别名 `scnet.work_dir`

可选资源字段：

- `scnet.nodes` / `scnet.nnode`
- `scnet.ppn` / `scnet.cpus_per_task`
- `scnet.gpus_per_node`
- `scnet.dcus_per_node`
- `scnet.memory` / `scnet.job_mem`
- `scnet.time_limit` / `scnet.wall_time`
- `scnet.job_name`

归一规则：

- `partition` 归一为 scnet-chat 的 `queue` / `--queue`。
- `remote_work_dir` 归一为 scnet-chat 的 `work_dir` / `--work-dir`。
- `time_limit` 归一为 `wall_time` / `--wall-time`。
- `memory` 归一为 `job_mem` / `--job-mem`。
- 若 `scnet.region` 存在，交接给 scnet-chat 时必须显式包含区域；可以先请求 `scnet-chat` 切换到该区域，或使用支持区域前缀的命令格式。
- 若 `runtime.scnet` 中缺少提交必需字段，立即转交 `onescience-runsite` 补齐配置，不能退回到 `runtime.cluster.*` 或 scnet-chat 默认值。

交接给 `scnet-chat` 的最小结构：

```json
{
  "config_source": "onescience.json.runtime.scnet",
  "region": "华东一区【昆山】",
  "queue": "comp",
  "work_dir": "~/oneskills-test/run01",
  "command": "bash run_job.slurm",
  "job_name": "run01",
  "resources": {
    "nnode": 1,
    "ppn": 2,
    "wall_time": "12:00:00"
  }
}
```

## Steps

1. 读取 `onescience.json.runtime.scnet`，归一 `region`、`partition`/`queue`、`remote_work_dir`/`work_dir` 和资源参数。
2. 先确定本地测试目录 `work_dir`，优先取 `runtime.script.work_dir`。
3. 远端根目录取 `scnet.remote_work_dir` 或 `scnet.work_dir`，例如 `~/oneskills-test`。
4. 取本地测试目录最后一个子目录名作为上传根名；例如 `tests/run01` 的最后子目录名是 `run01`。
5. 在远端创建 `scnet.remote_work_dir/<最后子目录名>/` 及其 `logs/` 子目录，并按相对路径上传本地测试目录中的所有文件；若后续使用 SLURM，`logs/` 必须在提交前存在。
6. 先优先询问 `scnet-chat` 是否可自动生成 `run_job.slurm`；如果可以，直接让 `scnet-chat` 在远端生成并提交。
7. 如果 `scnet-chat` 未自动生成 `run_job.slurm`，runtime2 必须参考 `./assets/templates/slurm_cpu.sh`、`./assets/templates/slurm_dcu.sh`、`./assets/templates/slurm_gpu.sh`、`./assets/templates/slurm_gpu_multinode_torchrun.sh` 或 `./assets/tpl.slurm`，再根据 `runtime.cluster.*`、`runtime.target.*`、`runtime.modules`、`runtime.script.*`、`runtime.env_vars.*` 和 `runtime.conda.enabled` 在本地生成同名脚本，并上传到同一远端目录。
8. 如果 `runtime.conda.enabled=true`，远端脚本中保留 `runtime.conda.activate_script`；如果 `runtime.conda.enabled=false`，远端脚本中跳过激活步骤。
9. 通过 `scnet-chat` 触发远端提交、状态查询和日志下载；提交命令必须包含来自 `onescience.json.runtime.scnet` 的区域、队列和工作目录，例如 `在{region}提交作业 bash run_job.slurm --queue {partition} --work-dir {scnet.remote_work_dir} --ppn {ppn} --wall-time {wall_time} --job-name {job_name}`。
10. 任务完成后，把远端测试目录或平台侧任务的 stdout/stderr 日志下载到本地测试目录的 `logs/`，即 `<work_dir>/logs/`；`local_log_dir` 必须输出该路径。不要下载到 `.onescience/logs/<job_name>/`。
11. 若发现是 `scnet.region`、`scnet.partition`、`scnet.remote_work_dir` 错误，上传根目录错误、入口路径不对、任务清单不完整、cluster/resource 字段错误等配置问题，暂停当前执行尝试并立即调用 `skills/onescience-runsite/SKILL.md`；无需向用户二次确认。runsite 成功后回到 `discover` 并继续原测试任务。
12. 若平台侧证据指向环境问题，例如解释器不存在、缺包、OneScience/torch 不可用或分布式运行时未就绪，暂停当前执行尝试并立即调用 `skills/onescience-installer/SKILL.md`；无需向用户二次确认。installer verify 成功后回到 `preflight` 并继续原测试任务。

## Upload Example

### 本地目录 `tests/run01`

- 本地：`tests/run01/code/train.py`
- 远端：`~/oneskills-test/run01/code/train.py`
- 本地：`tests/run01/run_job.slurm`
- 远端：`~/oneskills-test/run01/run_job.slurm`

### 通过 scnet-chat 执行

```text
调用 scnet-chat：
1. 使用 onescience.json.runtime.scnet.region 选择区域
2. 创建远端目录 ~/oneskills-test/run01/
3. 上传 tests/run01/ 下所有文件，保持相对路径
4. 使用 onescience.json.runtime.scnet.partition 作为 --queue 提交 run_job.slurm
5. 查询 task_id
6. 下载日志到 tests/run01/logs/
```

## Output

至少产出：

- `config_source`
- `region`
- `partition` 或 `queue`
- `submission_state`
- `execution_state`
- `task_id`
- `status_source`
- `log_state`
- `log_readiness`
- `local_log_dir`
- `synced_logs`
- `sync_status`
- `evidence.execute`

## Rules

- 不要在 runtime2 内重复实现 SCnet 平台工作流。
- 不要把平台侧连接中断、服务不可用或日志未就绪误判成业务代码失败。
- 排队阶段日志占位内容不算真实日志，应返回 `log_readiness=not_ready`。
- 自动委托 runsite/installer 成功解除阻断后，不要把修复结果作为最终输出；必须恢复 runtime 阶段并重新尝试执行原测试任务，且保持 SCnet 远程执行边界。
