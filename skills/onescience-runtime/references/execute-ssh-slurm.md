# Execute SSH SLURM

当 `execution_channel=ssh_slurm` 时读取本文件。

## Inputs

- `execution_channel=ssh_slurm`
- `submission_target`
- `runtime.conda`
- `runtime.modules.*`
- `runtime.script.work_dir`
- `runtime.script.code_path`
- `runtime.script.job_name`
- `runtime.ssh.work_dir`
- `runtime.ssh.*`
- `runtime.cluster.*`
- `runtime.target.*`
- `runtime.env_vars.*`
- `evidence.preflight`

## Steps

1. 先确定本地测试目录 `work_dir`，优先取 `runtime.script.work_dir`。
2. 先在本地生成 `run_job.slurm`，内容参考 `./assets/templates/slurm_cpu.sh`、`./assets/templates/slurm_dcu.sh`、`./assets/templates/slurm_gpu.sh`、`./assets/templates/slurm_gpu_multinode_torchrun.sh` 或 `./assets/tpl.slurm`，再由 `runtime.cluster.*`、`runtime.target.*`、`runtime.modules`、`runtime.script.*`、`runtime.env_vars.*` 和 `runtime.conda.enabled` 渲染。
3. 远端根目录取 `runtime.ssh.work_dir`，例如 `~/oneskills-test`。
4. 取本地测试目录的最后一个子目录名作为上传根名；例如 `tests/run01` 的最后子目录名是 `run01`。
5. 在远端创建 `runtime.ssh.work_dir/<最后子目录名>/`，并把本地目录中的文件按相对路径完整上传到这个目录下。
6. 如果 `runtime.conda.enabled=true`，远端脚本中保留 `runtime.conda.activate_script`；如果 `runtime.conda.enabled=false`，远端脚本中跳过激活步骤。
7. 如果 `runtime.modules` 非空，把每个 `module load <module>` 也按顺序写进远端脚本。
8. 上传 `run_job.slurm` 到同一远端目录。
9. 通过 SSH 在远端执行 `sbatch run_job.slurm`。
10. 通过远端 `squeue` / `sacct` 轮询任务状态。
11. 任务完成后，把远端日志下载到当前根目录的 `.onescience/logs/<job_name>/`。
12. 若远端 `sbatch`、`squeue`、`sacct` 或作业日志反馈 partition、GRES、`gpus_per_node`、`memory`、CPU、node 或 time limit 不可用，读取 `./references/slurm-resource-retry.md`，通过同一 SSH host 探测远端可用资源，临时重渲染并重新上传 `run_job.slurm` 后按预算重试；不要用本地 SLURM 信息替代远端证据，也不要直接写回 `onescience.json`。
13. 若资源探测后仍找不到兼容 partition 或资源，或调整会改变用户明确要求的并行规模，暂停当前执行尝试并立即调用 `skills/onescience-runsite/SKILL.md`；无需向用户二次确认。runsite 成功后回到 `discover` 并继续原测试任务。
14. 若发现是 SSH 连接字段缺失、`runtime.ssh.work_dir` 错误、入口路径不对、module 名称写错等非资源类配置问题，暂停当前执行尝试并立即调用 `skills/onescience-runsite/SKILL.md`；无需向用户二次确认。runsite 成功后回到 `discover` 并继续原测试任务。
15. 若远端执行阶段暴露出 conda 不可用、解释器缺失、缺包、OneScience/torch 不可导入或分布式运行时未就绪，暂停当前执行尝试并立即调用 `skills/onescience-installer/SKILL.md`；无需向用户二次确认。installer verify 成功后回到 `preflight` 并继续原测试任务。

## Upload Example

### 本地目录 `tests/run01`

- 本地：`tests/run01/code/train.py`
- 远端：`~/oneskills-test/run01/code/train.py`
- 本地：`tests/run01/run_job.slurm`
- 远端：`~/oneskills-test/run01/run_job.slurm`

### 提交与下载

```bash
ssh user@host "cd ~/oneskills-test/run01 && sbatch run_job.slurm"
ssh user@host "squeue -u user"
ssh user@host "sacct -j <job_id>"
rsync -a user@host:~/oneskills-test/run01/.onescience/logs/run01/ .onescience/logs/run01/
```

## Output

至少产出：

- `submission_state`
- `execution_state`
- `job_id`
- `submission_target`
- `local_log_dir`
- `synced_logs`
- `log_state`
- `sync_status`
- `evidence.execute`

## Rules

- 远程意图优先，不要在本地运行业务脚本替代远端验证。
- 不要在 execute 阶段重新猜测 SSH Host、partition 或工作目录。
- 只有远端 SLURM 反馈明确指向调度资源问题时，才允许按 `slurm-resource-retry.md` 临时调整 partition、`gpus_per_node`、memory 或其它资源并重试；所有调整必须记录在 `evidence.execute.slurm_adjustments`。
- 不要把临时资源覆盖直接写回 `onescience.json`；若调整后运行成功，最终输出建议用 `onescience-runsite` 持久化。
- 自动委托 runsite/installer 成功解除阻断后，不要把修复结果作为最终输出；必须恢复 runtime 阶段并重新尝试执行原测试任务，且保持远程执行边界。
- 若预检未确认 SSH 信息齐备，不要继续执行本工作流。
