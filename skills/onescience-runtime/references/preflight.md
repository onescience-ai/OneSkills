# Preflight

在 discover 已经派生出 `execution_channel` 后，读取本文件。

preflight 是进入 execute 的唯一门禁。只有本文件完成所有必需配置、入口、通道和环境 readiness 检查，并产出 `preflight_passed=true`、`execution_readiness=ready`、`evidence.preflight.status=passed`、`evidence.preflight.conda_checked=true`、`evidence.preflight.environment_checked=true` 后，runtime 才能读取 execute 分支。

## Read Inputs

1. 重新读取根目录 `onescience.json`。
2. 必读字段：
   - `runtime.conda`
   - `runtime.scnet.*`（SCnet 提交任务时必读）
   - `runtime.modules.*`
   - `runtime.script.work_dir`
   - `runtime.script.*`
   - `runtime.cluster.*`
   - `runtime.target.*`
   - `runtime.env_vars.*`
   - `runtime.ssh.work_dir`
   - `runtime.ssh.*`
   - `runtime.scnet.work_dir`
3. 保留 discover 产出的：
   - `execution_channel`
   - `semantic_environment_hints`
   - `submission_target_candidates`

## Conda Rules

runtime 只读取 `onescience.json.runtime.conda`；旧的顶层 `conda` 字段不再作为配置来源。

支持的最小结构只有两种：

```json
{
  "runtime": {
    "conda": {
      "enabled": true,
      "env_name": "onescience311",
      "activate_script": "source ~/.bashrc && conda activate onescience311"
    }
  }
}
```

或：

```json
{
  "runtime": {
    "conda": {
      "enabled": false
    }
  }
}
```

规则：

- `enabled=true` 时，脚本中才允许使用 `activate_script`；若缺失，则用 `env_name` 渲染最小激活命令。
- `enabled=false` 时，不激活 conda，只检查当前目标环境是否已可直接执行；仍需做轻量 readiness 检查。
- 若 `runtime.conda` 缺失、`runtime.conda.enabled` 缺失、`enabled=true` 但缺少 `env_name`，或按 `activate_script/env_name` 无法确认环境 ready，应立即委托 `onescience-installer` 安装或修复环境。
- 不得把缺失的 `runtime.conda` 自动解释为 `enabled=false`。`enabled=false` 只有在 `onescience.json.runtime.conda.enabled` 明确写出时才成立，且仍必须通过当前目标环境 readiness 检查。

## Mandatory Environment Discovery

preflight 必须通过当前 `execution_channel` 对目标环境做真实发现检查，并把结果写入 `evidence.preflight`：

- `conda_checked=true`：已读取并判定 `runtime.conda`，或已通过 installer 修复后重新读取。
- `environment_checked=true`：已按当前通道验证解释器、`onescience`、`torch` 和业务依赖 readiness。
- `channel_checked=true`：已验证本地、SSH、SLURM 或 SCnet 交接所需的最小通道条件。
- `entrypoint_checked=true`：已验证配置中声明的入口脚本或运行命令真实存在且不为空。

本地通道只能使用本地 shell 证据；SSH/远端 SLURM 通道必须通过 SSH 在远端执行探测；SCnet 通道必须通过 `runtime.scnet` 和 `scnet-chat` 可消费的显式交接信息确认。不得用本地 import、历史日志或自然语言线索替代目标环境发现结果。

任何一项检查未执行、无证据或失败时，设置 `preflight_passed=false`、`execution_readiness=blocked`，并根据阻断类型自动委托 `onescience-runsite` 或 `onescience-installer`。环境类阻断必须走 `onescience-installer`。

## SCnet Config Rules

当 `execution_channel=scnet_mcp` 且用户意图包含”提交新任务”时，runtime2 必须读取 `onescience.json.runtime.scnet`，并把它作为交给 `scnet-chat` 的提交参数来源。

推荐最小结构：

```json
{
  "runtime": {
    "scnet": {
      "region": "华东一区【昆山】",
      "partition": "comp",
      "remote_work_dir": "~/oneskills-test",
      "nodes": 1,
      "ppn": 2,
      "wall_time": "12:00:00",
      "job_name": "onescience-run"
    }
  }
}
```

规则：

- `region` 必须来自 `runtime.scnet.region`，用于 scnet-chat 的区域选择或区域化提交。
- `partition` 是 OneScience 侧规范字段；提交给 scnet-chat 时归一为 `queue` / `--queue`。若只存在 `scnet.queue`，可作为兼容别名读取，但输出仍记录 `partition`。
- `remote_work_dir` 与 `work_dir` 二选一；提交给 scnet-chat 时归一为 `--work-dir`。
- `nodes`/`nnode`、`ppn`/`cpus_per_task`、`gpus_per_node`、`dcus_per_node`、`memory`/`job_mem`、`time_limit`/`wall_time`、`job_name` 按 scnet-chat 支持的显式参数传递。
- 用户自然语言中的 region、partition 或 queue 只作为缺失字段线索；在未写入或确认到 `onescience.json.runtime.scnet` 前，不要据此提交任务。
- 若提交任务缺少 `scnet.region`、`scnet.partition`/`scnet.queue` 或 `scnet.remote_work_dir`/`scnet.work_dir`，设置 `next_action=onescience-runsite` 和 `blocking_reason=missing_scnet_submit_config`，由 runsite 补齐后再回到 `discover`。

## Channel-specific Checks

### `local_direct`

- 校验 `runtime.script.work_dir` 是否存在；缺失时可退回到 `runtime.script.code_path` 所在目录。
- 校验当前解释器可执行。
- 校验 `runtime.conda` 或当前环境下 `onescience`、`torch` 及业务入口依赖是否可导入。
- 若 `runtime.modules` 非空，确认这些 module 名称在当前环境中可加载。

### `local_slurm`

- 除入口与环境检查外，确认当前环境可直接调用：
  - `sbatch`
  - `squeue`
  - `sacct`
- 校验 `runtime.cluster.partition`、`nodes`、`cpus_per_task`、`time_limit` 等提交字段是否齐备。
- 校验测试目录可写，且 `run_job.slurm` 可生成到该目录。
- 不要求 preflight 提前穷尽验证 partition 与资源上限；若提交或运行阶段收到 SLURM 资源反馈，由 execute 读取 `./references/slurm-resource-retry.md` 处理。

### `ssh_slurm`

- 校验 `runtime.ssh.work_dir` 与 SSH 连接信息齐备。
- 校验远端工作目录、入口脚本、SLURM 提交所需字段是否齐备。
- readiness 检查必须通过 SSH / 远端通道确认，不要用本地 import 结果替代远端环境结论。
- 不要求 preflight 提前穷尽验证远端 partition 与资源上限；若提交或运行阶段收到远端 SLURM 资源反馈，由 execute 通过同一 SSH host 读取 `./references/slurm-resource-retry.md` 处理。

### `ssh_direct`

- 校验 `runtime.ssh.work_dir` 与 SSH 连接信息齐备。
- 校验本地测试目录、入口脚本、远端工作目录和远端写入权限是否齐备。
- readiness 检查必须通过 SSH / 远端通道确认，不要用本地 import 结果替代远端环境结论。
- 不要求 SLURM 字段或 `sbatch` / `squeue` / `sacct` 可用；该通道只做远端非调度直接执行。

### `scnet_mcp`

- 校验 `runtime.scnet.*` 中的必要平台接入和提交信息齐备。
- 若用户意图是提交新任务，确认本地测试目录、运行命令和提交清单存在。
- 若用户意图是提交新任务，确认 `scnet.region`、`scnet.partition`/`scnet.queue`、`scnet.remote_work_dir`/`scnet.work_dir` 可用，并准备交给 `scnet-chat` 的显式参数，不允许让 scnet-chat 自动选择默认区域或默认队列。
- 若用户意图是观察已有任务，确认 `task_id` 或其等价标识可用。
- 平台侧真实动作继续交给 `scnet-chat`，preflight 只判断交接是否完整。

## Entry and Readiness Rules

至少检查：

- 配置里声明的入口脚本是否真实存在于当前项目
- `enabled=true` 时 conda 是否可激活
- `enabled=false` 时当前目标解释器是否可运行 `import onescience` 与 `import torch`，且脚本不应插入 conda activate
- `runtime.modules` 是否为空或可加载
- 测试目录 / 远端工作目录是否可定位
- 通道要求的最小前置条件是否满足

若发现以下问题，统一自动委托 `onescience-installer`：

- 缺少 `runtime.conda`
- `runtime.conda.enabled` 缺失
- conda 激活失败
- 当前解释器不存在
- `import onescience` 失败
- `import torch` 失败
- 缺失业务运行所需包
- 分布式运行时未就绪

## Runtime Handoff

当环境未 ready 时，至少输出：

- `next_action=onescience-installer`
- `installer_reason`
- `resume_target=onescience-runtime`
- `resume_phase=preflight`
- `execution_context`
- `transport_context`
- `evidence.preflight`

随后立即加载并执行 `skills/onescience-installer/SKILL.md`；无需向用户二次确认，也不要在 runtime 中补装环境。环境修复并 verify 成功后，必须重新读取 `onescience.json.runtime.conda`，再从 `preflight` 继续后续阶段。

installer verify 成功不是最终任务完成信号。重新通过 preflight 后，必须继续进入对应 `execution_channel` 的 execute 分支，运行用户原始测试任务；只有 installer 阻断、verify 失败、需要用户补充信息，或恢复后的 preflight 发现新的真实阻断时，才停止。

## Output

preflight 至少产出：

- `execution_channel`
- `submission_target`
- `preflight_passed`
- `execution_readiness`
- `blocking_reason`
- `missing_fields`
- `confirmation_required`
- `installer_fallback_required`
- `evidence.preflight`

一句话原则：

preflight 负责回答“当前能不能执行、为什么不能、该继续执行还是自动委托 `onescience-installer`”，但不负责补装环境。
