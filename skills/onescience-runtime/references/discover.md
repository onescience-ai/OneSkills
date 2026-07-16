# Discover

每个 runtime 任务都先读取本文件。

## Steps

1. 读取项目根目录 `onescience.json`。
2. 读取 `runtime.execution_profile` 中以下字段：
   - `run_site`
   - `execution_mode`
   - `access_mode`
   - `execution_channel`（仅作对照证据）
3. 对三元组做有限归一：
   - `run_site` 只接受 `local` 或 `remote`
   - `execution_mode=slurm` 表示走调度执行
   - `execution_mode` 为空、`none`、`None` 或 `null` 时，视为非调度直接执行
   - `access_mode=scnet` 表示 SCnet 平台接入
   - `access_mode=ssh` 表示 SSH 接入
   - `run_site=local` 且 `access_mode` 为空、缺失、`none`、`None` 或 `null` 时，视为本地访问路径
   - 兼容旧写法时，只把它们归一到上述语义，不反向用旧字段驱动 routing
4. 用归一后的三元组派生 `execution_channel`：
   - `(local, none, empty)` -> `local_direct`
   - `(local, slurm, empty)` -> `local_slurm`
   - `(remote, none, ssh)` -> `ssh_direct`
   - `(remote, slurm, ssh)` -> `ssh_slurm`
   - `(remote, none, scnet)` -> `scnet_mcp`
   - `(remote, slurm, scnet)` -> `scnet_mcp`；SCnet 平台提交仍委托 `scnet-chat`，`execution_mode=slurm` 只表示需要消费队列/资源字段
5. 若 `onescience.json` 缺失、关键字段为空、归一后仍无法派生通道：
   - `next_action=onescience-runsite`
   - `blocking_reason=missing_runtime_config` / `unsupported_execution_tuple` / `config_tuple_conflict`
   - 立即加载并执行 `skills/onescience-runsite/SKILL.md` 补齐或生成运行站点配置；无需向用户二次确认。
   - runsite 成功补齐或确认配置后重新读取根目录 `onescience.json`，再从 `discover` 重新归一三元组，并继续原测试任务。
6. 读取用户意图与上游 handoff，只把 Host、partition、region、queue、accelerator、module、conda、path 等视为语义环境线索，不直接视为已确认环境事实。
   - 若后续会走 `scnet-chat` 提交任务，`region`、`partition`/`queue`、`remote_work_dir`/`work_dir` 的最终来源必须是 `onescience.json.runtime.scnet`，不要把自然语言中的区域名或队列名直接当成已确认提交目标。
7. 收集本阶段的最小输出，供 preflight 使用。

## Output

discover 至少产出：

- `run_site`
- `execution_mode`
- `access_mode`
- `execution_channel`
- `submission_target_candidates`
- `semantic_environment_hints`
- `missing_facts`
- `evidence.discovery`

## Rules

- 不要让旧的 `execution_channel` 反向覆盖三元组 routing。
- 不要在 discover 阶段执行安装、提交或真实业务运行。
- 不要把用户语义中的环境线索直接升级为最终提交目标。
- discover 只回答“走哪条链路、目前缺什么事实”。最终能否执行由 preflight 判定。
- `next_action=onescience-runsite` 是内部自动交接，不是用户确认提示。
- `onescience-runsite` 成功解除配置阻断后，不要以配置完成作为最终输出；必须回到 runtime 继续 `discover -> preflight -> execute -> diagnose`。
