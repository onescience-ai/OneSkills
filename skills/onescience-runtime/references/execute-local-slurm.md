# Execute Local SLURM

当 `execution_channel=local_slurm` 时读取本文件。

## Inputs

- `execution_channel=local_slurm`
- `submission_target`
- `onescience.json.runtime.conda`
- `runtime.modules.*`
- `runtime.script.work_dir`
- `runtime.script.code_path`
- `runtime.script.job_name`
- `runtime.cluster.*`
- `runtime.target.*`
- `runtime.env_vars.*`
- `evidence.preflight`

## Steps

1. 先确定测试目录 `work_dir`，优先取 `runtime.script.work_dir`。
2. 在测试目录生成 `run_job.slurm`，脚本内容参考 `./assets/templates/slurm_cpu.sh`、`./assets/templates/slurm_dcu.sh`、`./assets/templates/slurm_gpu.sh`、`./assets/templates/slurm_gpu_multinode_torchrun.sh` 或 `./assets/tpl.slurm`，再由 `runtime.cluster.*`、`runtime.target.*`、`runtime.modules`、`runtime.script.*`、`runtime.env_vars.*` 和 `runtime.conda.enabled` 渲染。
3. 如果 `runtime.conda.enabled=true`，在 `run_job.slurm` 中加入 `runtime.conda.activate_script`。
4. 如果 `runtime.conda.enabled=false`，在 `run_job.slurm` 中跳过 conda 激活，直接使用当前目标环境。
5. `runtime.modules` 中的 module 按顺序逐个写入 `module load <module>`。
6. 在 `work_dir` 中执行 `sbatch run_job.slurm`。
7. 使用 `squeue` / `sacct` 轮询任务状态。
8. 从本地或作业输出目录读取 `*.out` / `*.err`，并写入当前根目录的 `.onescience/logs/<job_name>/`。
9. 若 `sbatch`、`squeue`、`sacct` 或作业日志反馈 partition、GRES、`gpus_per_node`、`memory`、CPU、node 或 time limit 不可用，读取 `./references/slurm-resource-retry.md`，探测可用资源，临时重渲染 `run_job.slurm` 并按预算重试；不要直接写回 `onescience.json`。
10. 若资源探测后仍找不到兼容 partition 或资源，或调整会改变用户明确要求的并行规模，暂停当前执行尝试并立即调用 `skills/onescience-runsite/SKILL.md`；无需向用户二次确认。runsite 成功后回到 `discover` 并继续原测试任务。
11. 若发现是 `work_dir` 缺失、入口脚本路径错误、module 名称写错等非资源类配置问题，暂停当前执行尝试并立即调用 `skills/onescience-runsite/SKILL.md`；无需向用户二次确认。runsite 成功后回到 `discover` 并继续原测试任务。
12. 若执行中暴露出 conda/解释器不可用、缺包、OneScience/torch 不可导入、分布式运行时未就绪等环境问题，暂停当前执行尝试并立即调用 `skills/onescience-installer/SKILL.md`；无需向用户二次确认。installer verify 成功后回到 `preflight` 并继续原测试任务。

## Run Example

### 生成脚本并提交

```bash
cd tests/run01
cat > run_job.slurm <<'EOF'
#SBATCH -p hpctest01
#SBATCH -N 1
#SBATCH --gres=dcu:1
...
EOF
sbatch run_job.slurm
```

### 结果落盘

```bash
mkdir -p .onescience/logs/run01
cp *.out *.err .onescience/logs/run01/
```

## Output

至少产出：

- `submission_state`
- `execution_state`
- `job_id`
- `local_log_dir`
- `synced_logs`
- `log_state`
- `sync_status`
- `evidence.execute`

## Rules

- 不要在 execute 阶段重新选择执行通道。
- 只有 SLURM 反馈明确指向调度资源问题时，才允许按 `slurm-resource-retry.md` 临时调整 partition、`gpus_per_node`、memory 或其它资源并重试；所有调整必须记录在 `evidence.execute.slurm_adjustments`。
- 不要把临时资源覆盖直接写回 `onescience.json`；若调整后运行成功，最终输出建议用 `onescience-runsite` 持久化。
- 自动委托 runsite/installer 成功解除阻断后，不要把修复结果作为最终输出；必须恢复 runtime 阶段并重新尝试执行原测试任务。
- 若预检未确认 `sbatch/squeue/sacct` 可用，不要继续执行本工作流。
