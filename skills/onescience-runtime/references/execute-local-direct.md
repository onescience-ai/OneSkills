# Execute Local Direct

当 `execution_channel=local_direct` 时读取本文件。

## Inputs

- `execution_channel=local_direct`
- `submission_target`
- `runtime.conda`
- `runtime.modules.*`
- `runtime.script.work_dir`
- `runtime.script.code_path`
- `runtime.env_vars.*`
- `evidence.preflight`

## Steps

1. 先确定本地测试目录 `work_dir`：优先取 `runtime.script.work_dir`，缺失时回退到 `runtime.script.code_path` 所在目录。
2. 在测试目录生成任务执行脚本，脚本名优先使用 `run_job.sh`；脚本内容参考 `./assets/templates/local_direct.sh`，但按 `runtime.conda.enabled` 分支渲染。
3. 按 `runtime.modules` 的顺序逐个执行 `module load <module>`；例如：
   - `module load sghpc-mpi-gcc/26.3`
   - `module load sghpcdas/25.6`
4. 如果 `runtime.conda.enabled=true`，先执行 `runtime.conda.activate_script`，再进入测试目录。
5. 如果 `runtime.conda.enabled=false`，不要激活 conda，直接进入测试目录执行测试脚本。
6. 进入 `work_dir` 后，执行生成的 `run_job.sh` 或脚本里指定的测试脚本/等价入口命令。
7. 记录 stdout/stderr、退出码、产物文件和日志目录。
8. 默认把结果写到当前根目录的 `.onescience/logs/<job_name>/`，其中 `job_name` 优先取 `runtime.script.job_name`，否则用测试目录最后一级目录名。
9. 若发现是配置缺失、`work_dir` 不存在、脚本路径不对、`runtime.modules` 里引用了错误 module 名称等配置问题，暂停当前执行尝试并立即调用 `skills/onescience-runsite/SKILL.md`；无需向用户二次确认。runsite 成功后回到 `discover` 并继续原测试任务。
10. 若执行中出现 `python: command not found`、`ModuleNotFoundError`、`ImportError`、缺包、OneScience/torch 不可导入或分布式运行时未就绪，暂停当前执行尝试并立即调用 `skills/onescience-installer/SKILL.md`；无需向用户二次确认。installer verify 成功后回到 `preflight` 并继续原测试任务。

## Run Example

### 无 conda 环境

```bash
module load sghpc-mpi-gcc/26.3
module load sghpcdas/25.6
cd tests/run01
cat > run_job.sh <<'EOF'
#!/bin/bash
bash run_test.sh
EOF
bash run_job.sh 2>&1 | tee .onescience/logs/run01/stdout.log
```

### 需要切换 conda 环境

```bash
module load sghpc-mpi-gcc/26.3
module load sghpcdas/25.6
source ~/.bashrc && conda activate onescience311
cd tests/run01
cat > run_job.sh <<'EOF'
#!/bin/bash
python train.py
EOF
bash run_job.sh 2>&1 | tee .onescience/logs/run01/stdout.log
```

## Output

至少产出：

- `submission_state=submitted` 或 `failed`
- `execution_state=running` / `completed` / `failed`
- `log_state`
- `local_log_dir`
- `synced_logs`
- `sync_status`
- `evidence.execute`

## Rules

- 不要在 execute 阶段补装环境。
- 若用户原始意图是远程执行，不要误走本工作流。
- 自动委托 runsite/installer 成功解除阻断后，不要把修复结果作为最终输出；必须恢复 runtime 阶段并重新尝试执行原测试任务。
- 本工作流只回答“本地直接运行是否已执行、当前状态如何、日志落到哪里”。
