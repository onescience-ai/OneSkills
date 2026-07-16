# Execute SSH Direct

当 `execution_channel=ssh_direct` 时读取本文件。

## Inputs

- `execution_channel=ssh_direct`
- `submission_target`
- `runtime.conda`
- `runtime.modules.*`
- `runtime.script.work_dir`
- `runtime.script.code_path`
- `runtime.script.job_name`
- `runtime.ssh.work_dir`
- `runtime.ssh.*`
- `runtime.env_vars.*`
- `evidence.preflight`

## Steps

1. 先确定本地测试目录 `work_dir`，优先取 `runtime.script.work_dir`，缺失时回退到 `runtime.script.code_path` 所在目录。
2. 在本地测试目录生成 `run_job.sh`，内容参考 `./assets/templates/local_direct.sh`，并按 `runtime.conda.enabled` 分支渲染。
3. 远端根目录取 `runtime.ssh.work_dir`，例如 `~/oneskills-test`。
4. 取本地测试目录的最后一个子目录名作为上传根名；例如 `tests/run01` 的最后子目录名是 `run01`。
5. 在远端创建 `runtime.ssh.work_dir/<最后子目录名>/`，并把本地目录中的文件按相对路径完整上传到这个目录下。
6. 如果 `runtime.conda.enabled=true`，远端脚本中保留 `runtime.conda.activate_script`；如果 `runtime.conda.enabled=false`，远端脚本中跳过激活步骤。
7. 如果 `runtime.modules` 非空，把每个 `module load <module>` 也按顺序写进远端脚本。
8. 通过 SSH 在远端进入上传目录并执行 `bash run_job.sh`。
9. 记录远端 stdout/stderr、退出码、产物文件和日志目录。
10. 执行完成后，把远端日志下载到当前根目录的 `.onescience/logs/<job_name>/`，其中 `job_name` 优先取 `runtime.script.job_name`，否则用测试目录最后一级目录名。
11. 若发现是 SSH 连接字段缺失、`runtime.ssh.work_dir` 错误、远端工作目录不可写、入口路径不对、module 名称写错等配置问题，暂停当前执行尝试并立即调用 `skills/onescience-runsite/SKILL.md`；无需向用户二次确认。runsite 成功后回到 `discover` 并继续原测试任务。
12. 若远端执行阶段暴露出 conda 不可用、解释器缺失、缺包、OneScience/torch 不可导入或分布式运行时未就绪，暂停当前执行尝试并立即调用 `skills/onescience-installer/SKILL.md`；无需向用户二次确认。installer verify 成功后回到 `preflight` 并继续原测试任务。

## Run Example

### 本地目录 `tests/run01`

- 本地：`tests/run01/code/train.py`
- 远端：`~/oneskills-test/run01/code/train.py`
- 本地：`tests/run01/run_job.sh`
- 远端：`~/oneskills-test/run01/run_job.sh`

### 无 conda 环境

本地生成并上传的 `run_job.sh` 示例：

```bash
#!/bin/bash
set -euo pipefail

module load sghpc-mpi-gcc/26.3
module load sghpcdas/25.6

cd ~/oneskills-test/run01
mkdir -p .onescience/logs/run01
bash run_test.sh 2>&1 | tee .onescience/logs/run01/stdout.log
```

远端执行与日志下载：

```bash
ssh user@host "mkdir -p ~/oneskills-test/run01"
rsync -a tests/run01/ user@host:~/oneskills-test/run01/
ssh user@host "cd ~/oneskills-test/run01 && bash run_job.sh"
rsync -a user@host:~/oneskills-test/run01/.onescience/logs/run01/ .onescience/logs/run01/
```

### 需要切换 conda 环境

本地生成并上传的 `run_job.sh` 示例：

```bash
#!/bin/bash
set -euo pipefail

module load sghpc-mpi-gcc/26.3
module load sghpcdas/25.6
source ~/.bashrc && conda activate onescience311

cd ~/oneskills-test/run01
mkdir -p .onescience/logs/run01
python train.py 2>&1 | tee .onescience/logs/run01/stdout.log
```

远端执行与日志下载：

```bash
ssh user@host "mkdir -p ~/oneskills-test/run01"
rsync -a tests/run01/ user@host:~/oneskills-test/run01/
ssh user@host "cd ~/oneskills-test/run01 && bash run_job.sh"
rsync -a user@host:~/oneskills-test/run01/.onescience/logs/run01/ .onescience/logs/run01/
```

## Output

至少产出：

- `submission_state`
- `execution_state`
- `submission_target`
- `local_log_dir`
- `synced_logs`
- `log_state`
- `sync_status`
- `evidence.execute`

## Rules

- 远程意图优先，不要在本地运行业务脚本替代远端验证。
- 不要在 execute 阶段重新猜测 SSH Host 或工作目录。
- 不要读取或执行 SLURM 分支，也不要要求 `runtime.cluster.*` 字段齐备。
- 自动委托 runsite/installer 成功解除阻断后，不要把修复结果作为最终输出；必须恢复 runtime 阶段并重新尝试执行原测试任务，且保持远程执行边界。
- 若预检未确认 SSH 信息齐备，不要继续执行本工作流。
