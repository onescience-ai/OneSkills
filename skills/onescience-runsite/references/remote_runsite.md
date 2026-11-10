# 远程运行站点工作流

用于创建远程运行配置。进入本工作流的前提是根目录不存在 `onescience.json`，且用户选择远程运行。

本工作流禁止泛泛要求用户“提供 SSH/SCnet/cluster 信息”。补问时必须逐字段列出字段名、含义、默认值或是否可留空；可以逐项询问，也可以一次性列出完整字段清单。

## 1. 选择接入方式

远程接入方式优先按 `~/.ssh/config` 平台连接数自动判定（判定与弹窗硬规则见 `SKILL.md` “多远程工作台选择”段），不无条件先问 SSH/SCnet：

- 平台连接 ≤ 1 个（用户未自加 SSH）→ 默认 `run_site=remote`、`access_mode=mcp`，**不弹框、不补问凭据**，直接走 MCP 分支。
- 平台连接 ≥ 2 个（用户自加了 SSH）→ 弹工作台选择弹窗，首位固定为“平台默认（SCNet MCP 优先）”，其余为各 SSH 连接；选平台默认→ `access_mode=mcp`，选某 SSH→ `access_mode=ssh`。
- 仅当完全没有可用连接、需用户首次提供凭据时，才向用户问：

```text
远程运行准备通过 SSH 连接，还是通过 SCnet 连接？
```

- MCP（平台默认）：`run_site=remote`，`access_mode=mcp`
- SSH：`run_site=remote`，`access_mode=ssh`
- SCnet：`run_site=remote`，`access_mode=scnet`

用户选定接入方式后，立即进入对应分支。`access_mode=mcp` 无需任何凭据字段、不做远程连接验证（见第 1.1 节）；SSH/SCnet 分支才逐字段补问并验证。不要把连接字段和 Slurm 资源字段放在同一次补问中。`access_mode=scnet` 不再强制补齐 SSH 信息（如需回退能力由运行期 `~/.ssh/config` 现取）。

## 1.1 MCP 分支（平台优先）

`access_mode=mcp` 表示优先调用 OneCode 平台注入的 SCNet MCP 工具，调不通时回退读取 `~/.ssh/config` 走 SSH。该分支：

- **不补问、不写入任何凭据**：既不写 `runtime.ssh`，也不写 `runtime.scnet`（SCNet MCP 凭据由平台托管，不落盘）。
- **不做远程连接验证**：SCNet MCP 是 OneCode 侧能力，OneSkills 无法前置检测，连通与回退判定下放到 runtime 运行期“先试 MCP、调不通回退 SSH”。
- `accelerator_kind`：runsite 无法前置确定，交由 runtime 运行期探测或按任务上下文合理默认；若可从工作台选择弹窗的 probe 结果复用则更佳，但不得因此弹问用户。
- 确定 `access_mode=mcp` 后，直接跳到第 4 节“是否使用 Slurm”选择；`execution_mode=slurm` 时才补问/写入 `runtime.cluster`。

## 2. SSH 分支

读取 `assets/runsite_profiles/ssh_remote.json`，按空字段逐项询问：

| 字段 | 话术 |
|---|---|
| `host` / 别名 | 请提供 SSH Host 别名；没有则可留空自动生成。 |
| `hostname` | 请提供远程主机名或 IP。 |
| `port` | 请提供 SSH 端口；直接回车使用 22。 |
| `user` | 请提供 SSH 用户名。 |
| `identity_file` | 请提供 SSH 私钥路径。 |
| `remote_work_dir` | 请提供远程工作目录。 |

一次性补问时必须列出：

```text
请按下面字段提供 SSH 连接信息：
- host：SSH Host 别名；没有则可留空自动生成
- hostname：远程主机名或 IP
- port：SSH 端口；直接回车使用 22
- user：SSH 用户名
- identity_file：SSH 私钥路径
- remote_work_dir：远程工作目录
```

保存 SSH 配置：

```bash
python skills/onescience-runsite/scripts/ssh_config.py add \
  --host <hostname> --port <port> --user <user> \
  --identity <identity_file> --alias <alias>
```

保存后必须验证 SSH 是否能连接远程：

```bash
python skills/onescience-runsite/scripts/ssh_config.py check --alias <alias> --max-attempts 3
```

验证规则：

- 最多尝试 3 次。
- 若出现私钥权限过宽错误，例如 `Permissions for '<IdentityFile>' are too open`、`bad permissions`，使用 `icacls <IdentityFile> /grant:r <当前 Windows 用户>:F` 修复后重试。典型命令：

```powershell
icacls C:\Users\Administrator\.ssh\acrl99olqh_dzeshell.hpccube.com_RsaKeyExpireTime_2026-10-13_10-18-30.txt /grant:r Administrator:F
```

- 若是其它 SSH 登录异常，可做一次明确、低风险的修复或重试；超过 3 次仍无法连接时停止，不继续生成最终配置。
- 最终仍失败时，告诉用户：“提供的信息无法连接上远程，请按 SSH 字段清单重新提交远程连接信息”，并列出 `host`、`hostname`、`port`、`user`、`identity_file`、`remote_work_dir`。
- SSH 验证成功后，才进入“是否使用 Slurm”选择。

## 3. SCnet 分支

读取 `assets/runsite_profiles/scnet_remote.json`，按空字段逐项询问：

| 字段 | 话术 |
|---|---|
| `SCNET_ACCESS_KEY` | 请提供 SCNET_ACCESS_KEY；我不会在输出中回显明文。 |
| `SCNET_SECRET_KEY` | 请提供 SCNET_SECRET_KEY；我不会在输出中回显明文。 |
| `SCNET_USER` | 请提供 SCnet 用户名。 |
| `region` | 请提供 SCnet 区域，例如核心节点、华东一区【昆山】等。 |
| `remote_work_dir` | 请提供远程工作目录。 |

一次性补问时必须列出：

```text
请按下面字段提供 SCnet 连接信息：
- SCNET_ACCESS_KEY：SCnet access key；我不会在输出中回显明文
- SCNET_SECRET_KEY：SCnet secret key；我不会在输出中回显明文
- SCNET_USER：SCnet 用户名
- region：SCnet 区域，例如核心节点、华东一区【昆山】等
- remote_work_dir：远程工作目录
```

保存 SCnet 凭据：

```bash
python skills/onescience-runsite/scripts/scnet_config.py set \
  --access-key <key> --secret-key <secret> --user <user> --region <region>
```

保存后必须尝试 SCnet 登录验证：

```bash
python skills/onescience-runsite/scripts/scnet_config.py check-login
```

SCnet 验证只检查凭据能否获取 token，不提交作业、不管理文件。若无法登录，停止流程并告诉用户：“提供的信息无法连接上远程，请按 SCnet 字段清单重新提交远程连接信息”，并列出 `SCNET_ACCESS_KEY`、`SCNET_SECRET_KEY`、`SCNET_USER`、`region`、`remote_work_dir`。

SCnet 登录验证成功后，即可进入第 4 节“是否使用 Slurm”选择；`access_mode=scnet` 不再强制补问与验证 SSH（如需 SSH 回退能力由运行期 `~/.ssh/config` 现取）。

## 4. Slurm 选择与字段

连接信息完成并验证通过（`access_mode=ssh`/`access_mode=scnet`）后，或 `access_mode=mcp` 确定接入方式后，再问：

```text
是否使用 Slurm 提交任务？
```

- 是：`execution_mode=slurm`，继续补问 Slurm 集群资源信息。
- 否：`execution_mode=null`，`runtime.cluster=null`，不要补问 Slurm 资源字段。

只有当 `execution_mode=slurm` 时，读取 `assets/cluster_profliles/slurm.json` 并补问：

| 字段 | 默认值 |
|---|---|
| `partition` | 无 |
| `nodes` | `1` |
| `gpus_per_node` | `1` |
| `cpus_per_task` | `8` |
| `memory` | `64GB` |
| `time_limit` | `02:00:00` |
| `gpu_type` | 检测或确认的 `accelerator_kind` |
| `ntasks_per_node` | `1` |

带默认值的字段必须告诉用户可以直接回车使用默认值。

一次性补问时必须列出：

```text
请按下面字段提供 Slurm 集群资源信息：
- partition：Slurm 分区名称，例如 gpu、compute、hpctest01；无默认值
- nodes：节点数量；直接回车使用 1
- gpus_per_node：每个节点需要的 GPU/DCU 数量；直接回车使用 1
- cpus_per_task：每个任务需要的 CPU 核心数；直接回车使用 8
- memory：内存大小，例如 64GB；直接回车使用 64GB
- time_limit：作业时间限制 HH:MM:SS；直接回车使用 02:00:00
- gpu_type：Slurm 加速器类型；直接回车使用后续检测或用户确认的 dcu/gpu
- ntasks_per_node：每节点任务数；直接回车使用 1
```

不要把 SCnet、SSH 连接字段与 Slurm 集群资源字段合并成一次性补问。连接字段必须先完成，Slurm 字段只能在用户确认使用 Slurm 后再问。

## 5. 硬件检测与 modules

当 `access_mode=ssh`/`access_mode=scnet` 连接信息完成并验证通过、且 Slurm 选择与资源字段也已完成后，必须检测远程运行平台的加速器类型（`access_mode=mcp` 跳过本阶段，`accelerator_kind` 下放到 runtime 运行期）：

```bash
python skills/onescience-runsite/scripts/runsite_config.py detect-hardware --ssh-alias <alias>
```

若输出 `hardware_detected=true` 且 `accelerator_kind` 为 `dcu` 或 `gpu`，后续 `generate` 必须传入对应的 `--accelerator-kind`。

若输出 `hardware_detected=false`，不要生成配置，必须询问用户：

```text
未能自动检测到远程运行平台加速器类型，请确认是 dcu 还是 gpu。
```

用户确认后，使用确认值作为 `--accelerator-kind`。脚本会从 `assets/hardware_profiles/{dcu|gpu}_hardware_profiles.json` 匹配 profile，并把 `software.modules` 写入 `onescience.json.runtime.modules`。不要手写 modules，除非用户明确覆盖。

只允许做上述硬件类型检测；不要在 runsite 中执行远端 `module avail`、`conda` 检查、Slurm 队列检查或提交作业。

## 6. 生成配置示例

### SSH 直连，不使用 Slurm

```bash
python skills/onescience-runsite/scripts/runsite_config.py --config-path ./onescience.json generate \
  --run-site remote \
  --execution-mode none \
  --access-mode ssh \
  --accelerator-kind dcu \
  --ssh-data '{"host":"my-cluster","hostname":"192.168.1.100","port":22,"user":"alice","identity_file":"~/.ssh/id_rsa","remote_work_dir":"/home/alice/work"}'
```

### SSH 连接，使用 Slurm

```bash
python skills/onescience-runsite/scripts/runsite_config.py --config-path ./onescience.json generate \
  --run-site remote \
  --execution-mode slurm \
  --access-mode ssh \
  --accelerator-kind dcu \
  --ssh-data '{"host":"my-cluster","hostname":"192.168.1.100","port":22,"user":"alice","identity_file":"~/.ssh/id_rsa","remote_work_dir":"/home/alice/work"}' \
  --cluster-data '{"partition":"hpctest01","nodes":1,"gpus_per_node":1,"cpus_per_task":8,"memory":"64GB","time_limit":"02:00:00","gpu_type":"dcu","ntasks_per_node":1}'
```

### SCnet 直连，不使用 Slurm

```bash
python skills/onescience-runsite/scripts/runsite_config.py --config-path ./onescience.json generate \
  --run-site remote \
  --execution-mode none \
  --access-mode scnet \
  --accelerator-kind dcu \
  --scnet-data '{"SCNET_ACCESS_KEY":"<key>","SCNET_SECRET_KEY":"<secret>","SCNET_USER":"alice","region":"核心节点","remote_work_dir":"~/work"}' \
  --ssh-data '{"host":"my-cluster","hostname":"192.168.1.100","port":22,"user":"alice","identity_file":"~/.ssh/id_rsa","remote_work_dir":"/home/alice/work"}'
```

### SCnet 连接，使用 Slurm

```bash
python skills/onescience-runsite/scripts/runsite_config.py --config-path ./onescience.json generate \
  --run-site remote \
  --execution-mode slurm \
  --access-mode scnet \
  --accelerator-kind dcu \
  --scnet-data '{"SCNET_ACCESS_KEY":"<key>","SCNET_SECRET_KEY":"<secret>","SCNET_USER":"alice","region":"核心节点","remote_work_dir":"~/work"}' \
  --ssh-data '{"host":"my-cluster","hostname":"192.168.1.100","port":22,"user":"alice","identity_file":"~/.ssh/id_rsa","remote_work_dir":"/home/alice/work"}' \
  --cluster-data '{"partition":"hpctest01","nodes":1,"gpus_per_node":1,"cpus_per_task":8,"memory":"64GB","time_limit":"02:00:00","gpu_type":"dcu","ntasks_per_node":1}'
```

### MCP（平台优先）直连，不使用 Slurm

不传 `--ssh-data`/`--scnet-data`（凭据由平台托管、不落盘）；`--accelerator-kind` 可取工作台弹窗 probe 结果或合理默认，确实未知时可省略并交由 runtime 运行期探测。

```bash
python skills/onescience-runsite/scripts/runsite_config.py --config-path ./onescience.json generate \
  --run-site remote \
  --execution-mode none \
  --access-mode mcp
```

### MCP（平台优先）连接，使用 Slurm

```bash
python skills/onescience-runsite/scripts/runsite_config.py --config-path ./onescience.json generate \
  --run-site remote \
  --execution-mode slurm \
  --access-mode mcp \
  --cluster-data '{"partition":"hpctest01","nodes":1,"gpus_per_node":1,"cpus_per_task":8,"memory":"64GB","time_limit":"02:00:00","gpu_type":"dcu","ntasks_per_node":1}'
```

## 7. 完成后回传

远程配置生成或复用完成后，`onescience-runsite` 只返回配置交接，不提交作业、不继续探测远端环境。若本次是被某个技能调用来补齐配置，`next_action` 指向调用技能；若没有调用方，`next_action` 指向 `onescience-orchestrator`，让 orchestrator 规划下一步。远程连接验证失败时仍然 `next_action=ask_user`。
