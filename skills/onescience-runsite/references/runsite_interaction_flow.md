# 运行站点交互流程

本文件只提供中文补问顺序和话术。字段契约见 `runsite_contract.md`，本地/远程执行细节见对应工作流。

## 1. 总顺序

```text
检查 ./onescience.json
  ├─ 存在且完整：展示摘要 -> 询问是否复用 -> 交接
  ├─ 存在但不完整：展示缺失字段 -> 只补问缺失字段 -> 修改 -> 交接
  └─ 不存在：询问本地/远程
        ├─ 本地：本地工作流
        └─ 远程：远程工作流
```

执行本流程时必须先完成上述分支判断，再读取当前分支对应的工作流文件；不要在开始时一次性读取全部参考文档。

## 1.1 补问硬规则

禁止使用模糊补问：

- 不要只说“请提供 SSH 信息”。
- 不要只说“请提供 SCnet 信息”。
- 不要只说“请提供 cluster 信息”或“请提供集群信息”。

需要用户补充信息时，必须采用下面两种方式之一：

1. 逐字段询问，每次明确字段名、含义、默认值或是否可留空。
2. 一次性给出字段清单，让用户按清单填写；清单必须列出所有需要的字段。

远程配置必须按阶段补问：

1. 先确认接入方式：SSH 或 SCnet。
2. 用户选定 SSH 后，立刻只补问 SSH 连接字段并验证连接；不要同时补问 Slurm 字段。
3. 用户选定 SCnet 后，立刻只补问 SCnet 连接字段并验证登录；不要同时补问 SSH 字段或 Slurm 字段。
4. SCnet 登录验证成功后，继续单独补问 SSH 连接字段并验证 SSH；远程执行必须补齐 SSH 信息。
5. 连接信息完成后，再询问是否使用 Slurm。
6. 只有用户回答使用 Slurm，才补问 Slurm 集群资源字段。

不要出现“需要提供 SCnet 连接信息、SSH 连接信息和 Slurm 集群资源信息，请一次性填写以下字段”这类把不同阶段信息混在一起的补问。

已有 `onescience.json` 不完整时，只能补问缺失字段，但仍必须逐一列出缺失字段。远程连接验证失败后要求用户重新提交连接信息时，也必须列出 SSH 或 SCnet 所需字段。

## 2. 已有配置话术

```text
检测到根目录已有运行站点配置文件 onescience.json：
- 运行站点：{run_site}
- 调度方式：{execution_mode}
- 接入方式：{access_mode}
- 硬件类型：{accelerator_kind} ({accelerator_vendor})
- SSH Host：{ssh_host_alias}
- SCnet 用户：{scnet_user}
- Slurm 分区：{partition}

是否按此配置继续？
```

用户回答：

- “是/确认/复用”：输出交接信息。
- “修改 XXX”：只修改指定字段。
- “重新配置”：提示先删除或重命名现有 `onescience.json`。

若已有配置是 `run_site=remote`，在输出交接信息前必须先做连接验证：

- 始终运行 `ssh_config.py check --alias <ssh_host_alias> --max-attempts 3`。
- `access_mode=scnet` 时，还要运行 `scnet_config.py check-login`。
- 验证失败时停止，不输出 runtime/installer 交接，告知“提供的信息无法连接上远程，请按下面字段重新提交远程连接信息”，并按失败的验证类型列出字段：SSH 验证失败列 SSH 字段，SCnet 验证失败列 SCnet 字段。

## 3. 新建配置第一问

当 `onescience.json` 不存在时，第一问必须是：

```text
你这次是本地运行还是远程运行？
```

不要提前询问 SSH、SCnet 或 Slurm。

## 4. 本地话术

```text
请提供本地工作目录；直接回车则使用当前项目目录。
```

若检测到本地 Slurm：

```text
检测到本地有 Slurm，是否使用 Slurm 提交任务？
```

本地配置固定：

```json
{
  "run_site": "local",
  "execution_mode": "slurm|null",
  "access_mode": ""
}
```

本地分支不要询问远程凭据。

## 5. 远程话术

远程第一问：

```text
远程运行准备通过 SSH 连接，还是通过 SCnet 连接？
```

远程配置：

```json
{
  "run_site": "remote",
  "execution_mode": "slurm|null",
  "access_mode": "ssh|scnet"
}
```

### SSH 字段

逐项询问：

1. `请提供 SSH Host 别名；没有则可留空自动生成。`
2. `请提供远程主机名或 IP。`
3. `请提供 SSH 端口；直接回车使用 22。`
4. `请提供 SSH 用户名。`
5. `请提供 SSH 私钥路径。`
6. `请提供远程工作目录。`

也可以一次性列出清单：

```text
请按下面字段提供 SSH 连接信息：
- host：SSH Host 别名；没有则可留空自动生成
- hostname：远程主机名或 IP
- port：SSH 端口；直接回车使用 22
- user：SSH 用户名
- identity_file：SSH 私钥路径
- remote_work_dir：远程工作目录
```

保存 SSH 配置后必须验证连接。若出现 `Permissions for '<IdentityFile>' are too open` 或 `bad permissions`，先用 `icacls <IdentityFile> /grant:r <当前 Windows 用户>:F` 修复，再重试。最多尝试 3 次；仍失败时停止，并列出 SSH 字段清单要求用户重新提交远程连接信息。

### SCnet 字段

逐项询问：

1. `请提供 SCNET_ACCESS_KEY；我不会在输出中回显明文。`
2. `请提供 SCNET_SECRET_KEY；我不会在输出中回显明文。`
3. `请提供 SCnet 用户名。`
4. `请提供 SCnet 区域，例如核心节点、华东一区【昆山】等。`
5. `请提供远程工作目录。`

也可以一次性列出清单：

```text
请按下面字段提供 SCnet 连接信息：
- SCNET_ACCESS_KEY：SCnet access key；我不会在输出中回显明文
- SCNET_SECRET_KEY：SCnet secret key；我不会在输出中回显明文
- SCNET_USER：SCnet 用户名
- region：SCnet 区域，例如核心节点、华东一区【昆山】等
- remote_work_dir：远程工作目录
```

保存 SCnet 凭据后必须尝试登录验证。无法登录时停止，并列出 SCnet 字段清单要求用户重新提交远程连接信息。

SCnet 登录验证成功后，必须继续按 SSH 字段清单补问并验证 SSH；远程执行必须具备 SSH 信息。

## 6. Slurm 选择与字段

SSH 连接验证成功后，才询问：

```text
是否使用 Slurm 提交任务？
```

仅当 `execution_mode=slurm` 时逐项询问：

| 顺序 | 字段 | 默认值 | 话术 |
|---|---|---:|---|
| a | `cluster.partition` | 无 | 请提供 Slurm 分区名称，例如 gpu、compute、hpctest01。 |
| b | `cluster.nodes` | `1` | 请提供节点数量；直接回车使用 1。 |
| c | `cluster.gpus_per_node` | `1` | 请提供每个节点需要的 GPU/DCU 数量；直接回车使用 1。 |
| d | `cluster.cpus_per_task` | `8` | 请提供每个任务需要的 CPU 核心数；直接回车使用 8。 |
| e | `cluster.memory` | `64GB` | 请提供内存大小，例如 64GB；直接回车使用 64GB。 |
| f | `cluster.time_limit` | `02:00:00` | 请提供作业时间限制 HH:MM:SS；直接回车使用 02:00:00。 |
| g | `cluster.gpu_type` | `dcu` | 请提供加速器类型，例如 dcu、gpu、a100；直接回车使用 dcu。 |
| h | `cluster.ntasks_per_node` | `1` | 请提供每节点任务数；直接回车使用 1。 |

也可以一次性列出清单：

```text
请按下面字段提供 Slurm 集群资源信息：
- partition：Slurm 分区名称，例如 gpu、compute、hpctest01；无默认值
- nodes：节点数量；直接回车使用 1
- gpus_per_node：每个节点需要的 GPU/DCU 数量；直接回车使用 1
- cpus_per_task：每个任务需要的 CPU 核心数；直接回车使用 8
- memory：内存大小，例如 64GB；直接回车使用 64GB
- time_limit：作业时间限制 HH:MM:SS；直接回车使用 02:00:00
- gpu_type：加速器类型，例如 dcu、gpu、a100；直接回车使用 dcu
- ntasks_per_node：每节点任务数；直接回车使用 1
```

## 7. 密钥输出

任何摘要、交接信息、日志和最终答复中都不要输出：

- `SCNET_ACCESS_KEY` 明文
- `SCNET_SECRET_KEY` 明文
- SSH 私钥内容

可以输出：

- SSH Host 别名
- SCnet 用户名
- 私钥文件路径

