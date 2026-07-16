# 检查已有配置工作流

用于检查、复用或按用户要求修改根目录 `onescience.json`。

## 1. 检查

```bash
python skills/onescience-runsite/scripts/runsite_config.py --config-path ./onescience.json check
```

若不存在：

- 输出 `config_exists=false`。
- 转到 `local_runsite.md` 或 `remote_runsite.md`。
- 第一问必须是“你这次是本地运行还是远程运行？”

若存在且完整：

- 展示非敏感摘要。
- 询问“是否按此配置继续？”
- 若 `run_site=local`，用户确认时直接输出交接信息。
- 若 `run_site=remote`，用户确认后先按 `access_mode` 做连接验证：
  - 始终运行 `python skills/onescience-runsite/scripts/ssh_config.py check --alias <ssh_host_alias> --max-attempts 3`。
  - `access_mode=scnet` 时，还要运行 `python skills/onescience-runsite/scripts/scnet_config.py check-login`。
  - 验证失败时停止，告知“提供的信息无法连接上远程，请按当前接入方式的字段清单重新提交远程连接信息”，并列出 SSH 或 SCnet 所需字段。
  - 验证成功后再输出交接信息。
  - 输出交接信息时优先回到调用 `onescience-runsite` 的技能；若没有明确调用方，则 `next_action=onescience-orchestrator`。不要因为配置完整而默认进入 runtime 或 installer。

若存在但不完整：

- 展示缺失字段。
- 只补问缺失字段；不要删除或重建文件。
- 补问时必须逐一列出缺失字段名、含义、默认值或是否可留空；不要只说“请提供 SSH 信息”“请提供 SCnet 信息”或“请提供 cluster 信息”。
- 若远程连接字段和 Slurm cluster 字段同时缺失，必须分阶段补问：先补齐并验证连接字段，再询问或补问 Slurm cluster 字段。
- 当 `run_site=remote` 且 `access_mode=scnet` 时，如果 SCnet 字段和 SSH 字段都缺失，先补问 SCnet 字段并验证登录，再补问 SSH 字段并验证连接；不要把两类字段合并在同一次补问中。
- 不要把连接字段和 Slurm cluster 字段合并成一次性补问。
- 如果缺失字段属于 SSH，按需列出：`runtime.ssh.host`/别名、`runtime.ssh.hostname`、`runtime.ssh.port`、`runtime.ssh.user`、`runtime.ssh.identity_file`、`runtime.ssh.remote_work_dir`。
- 如果缺失字段属于 SCnet，按需列出：`runtime.scnet.SCNET_ACCESS_KEY`、`runtime.scnet.SCNET_SECRET_KEY`、`runtime.scnet.SCNET_USER`、`runtime.scnet.region`、`runtime.scnet.remote_work_dir`。
- 如果缺失字段属于 Slurm cluster，按需列出：`runtime.cluster.partition`、`runtime.cluster.nodes`、`runtime.cluster.gpus_per_node`、`runtime.cluster.cpus_per_task`、`runtime.cluster.memory`、`runtime.cluster.time_limit`、`runtime.cluster.gpu_type`、`runtime.cluster.ntasks_per_node`。

## 2. 摘要字段

只展示：

- `runtime.execution_profile.run_site`
- `runtime.execution_profile.execution_mode`
- `runtime.execution_profile.access_mode`
- 硬件类型和厂商
- SSH Host 别名或 SCnet 用户名
- Slurm 分区、节点数、每节点加速器数

不要展示：

- `SCNET_ACCESS_KEY`
- `SCNET_SECRET_KEY`
- SSH 私钥内容

## 3. 修改已有配置

只有用户明确指定字段时才修改：

```bash
python skills/onescience-runsite/scripts/runsite_config.py --config-path ./onescience.json modify \
  --field runtime.cluster.partition \
  --value hpctest01
```

修改后再次运行 `check`，确认组合仍合法。

## 4. 不允许

- 用户说“重新配置”时直接覆盖 `onescience.json`。
- 重新生成整个文件来完成单字段修改。
- 用旧字段 `execution_channel` 修复新版配置。

若用户坚持重新配置，提示用户先删除或重命名现有 `onescience.json`。
