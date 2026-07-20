---
name: onescience-runsite
description: 解析、校验、保存和复用 OneScience 运行站点配置。用于任意技能在继续执行任务前补齐运行站点配置，完成配置发现、缺失字段补问、已有配置复用、remote 连接验证、运行平台 DCU/GPU 类型确认、modules 写入和结构化回传。不做安装、不提交作业、不执行运行、不做远端环境诊断。
type: executor
---

# OneScience 运行站点

`onescience-runsite` 是独立的配置工作流。它只负责把用户的运行位置、调度方式、接入方式、账号信息和资源提示整理成项目根目录的
`onescience.json`，然后把交接信息交回调用它的技能；若没有明确调用方，交回 `onescience-orchestrator` 让其规划下一步。

## 先读哪个

强制先读 `references/runsite_interaction_flow.md`，并按其中的分支顺序推进。不要一次性并行读取所有参考文件，也不要在没有命中分支前加载本地、远程、检查和契约等全部文档。

执行顺序必须是：

1. 先检查 `./onescience.json`。
2. 按 `runsite_interaction_flow.md` 判断分支：存在且完整、存在但不完整、不存在。
3. 只读取当前分支需要的一个工作流文件。
4. 若当前分支还需要字段含义或交接格式，再读取 `runsite_contract.md`。

| 任务                           | 读取                                             |
|------------------------------|------------------------------------------------|
| 入口顺序、分支判断、中文补问顺序                  | `references/runsite_interaction_flow.md`       |
| 职责边界、字段含义、交接格式               | `references/runsite_contract.md`               |
| 检查、复用或修改已有 `onescience.json` | `references/check_existing_config.md` |
| 创建本地配置                       | `references/local_runsite.md`         |
| 创建远程配置，包含 SSH 或 SCnet        | `references/remote_runsite.md`        |

## 补问硬规则

- 不允许只说“请提供 SSH 信息”“请提供 SCnet 信息”“请提供 cluster 信息”。
- 需要用户提供信息时，必须逐一列出字段名、含义、是否可留空或默认值。
- 可以逐字段一问一答，也可以给出一个字段清单让用户一次性填写；但字段清单必须完整。
- 远程配置必须分阶段补问：先让用户在 SSH 和 SCnet 中选择一种接入方式；用户选定后，立刻只补问该接入方式的连接信息并完成连接验证；连接信息完成后，才询问是否使用 Slurm。
- 远程执行必须补齐 SSH 信息；如果用户选择 SCnet，先补问 SCnet 连接字段并验证登录，再补问 SSH 连接字段并验证 SSH，然后才询问是否使用 Slurm。
- 如果用户选择 SCnet，只能先补问 SCnet 连接字段；不要同时补问 SSH 字段或 Slurm 集群资源字段。SCnet 验证完成后，再单独补问 SSH 字段。
- 如果用户选择 SSH，只能先补问 SSH 连接字段；不要同时补问 Slurm 集群资源字段。
- 只有用户明确选择使用 Slurm 后，才补问 Slurm 集群资源字段。
- 已有 `onescience.json` 不完整时，必须先根据 `run_site`、`execution_mode`、`access_mode` 判断哪些配置块是必填，再只补问这些必填块中缺失的字段；补问时仍必须列出每个缺失字段。
- 远程连接验证失败后，要求用户重新提交信息时，也必须列出对应接入方式需要重新提供的字段。
- 只要 `run_site=remote`，都必须校验并补齐 SSH 字段：`host`/别名、`hostname`、`port`、`user`、`identity_file`、`remote_work_dir`。
- 只要 `run_site=remote` 且 `access_mode=scnet`，都必须额外校验并补齐 SCnet 字段：`SCNET_ACCESS_KEY`、`SCNET_SECRET_KEY`、`SCNET_USER`、`region`、`remote_work_dir`。
- 只要 `execution_mode=slurm`，都必须校验并补齐 Slurm 字段：`partition`、`nodes`、`gpus_per_node`、`cpus_per_task`、`memory`、`time_limit`、`gpu_type`、`ntasks_per_node`。
- 用户提供完整运行信息后，必须检测对应运行平台加速器类型：本地直接/本地 Slurm 检测本机；远程 SSH 直接/远程 SSH Slurm 通过已验证 SSH Host 别名检测远程。若未检测出，先询问用户确认 `dcu` 还是 `gpu`，再生成配置。

有脚本时优先用 `scripts/runsite_config.py`、`scripts/ssh_config.py`、`scripts/scnet_config.py`。

## 字段所有权

`onescience-runsite` 只负责以下 `onescience.json` 字段的创建和更新：

**必须管理的字段：**
- `runtime.execution_profile`（`run_site`、`execution_mode`、`access_mode`）
- `runtime.ssh`（当 `run_site=remote` 时）
- `runtime.scnet`（当 `access_mode=scnet` 时）
- `runtime.cluster`（当 `execution_mode=slurm` 时）
- `runtime.target`（平台类型、硬件类型）
- `runtime.environment`（CPU 和加速器环境信息）
- `runtime.modules`（环境模块列表）
- `runtime.resources`（资源配置）
- `runtime.env_vars`（环境变量）

**禁止管理的字段：**
- `runtime.conda`：由 `onescience-installer` 技能独占管理

**行为规则：**
- 首次生成 `onescience.json` 时，只写入本技能负责的字段，不写入 `runtime.conda`
- 更新已有 `onescience.json` 时，只更新本技能负责的字段，保留其他技能写入的字段
- 检查配置完整性时，不验证 `runtime.conda` 字段（由 installer 负责验证）

## 新版配置三元组

`runtime.execution_profile` 只使用下面三个字段：

```json
{
  "run_site": "local|remote",
  "execution_mode": "slurm|null",
  "access_mode": "ssh|scnet|"
}
```

规则：

- `run_site` 只能是 `local` 或 `remote`。
- `execution_mode` 只能是 `slurm` 或  `null`。
- `access_mode` 只能是 `ssh` 或 `scnet`；当 `run_site=local` 时必须为空字符串 `""`。
- 不再生成或依赖 `execution_channel`。
- 不再把 `remote_slurm`、`remote_direct`、`cloud_api` 这些旧值写入新配置。

## 硬边界

禁止：

- 安装环境：`conda create`、`pip install`、`git clone`、`bash install.sh`
- 提交或运行作业：`sbatch`、`srun`、训练脚本、推理脚本
- 除连接验证和有限 DCU/GPU 类型检测外做远端就绪探测：远端 `sbatch`、`squeue`、`sacct`、module/conda 检查、远端可写性检查
- 提交任务或调用 `scnet-chat` 执行任务
- 明文输出 SCnet 密钥
- 重新创建已存在的项目根目录 `onescience.json`
- 创建临时 JSON 中间文件，例如 `cluster_data.json`、`run_site_data.json`、`temp_*_data.json`
- 写入或更新 `runtime.conda` 字段：该字段由 `onescience-installer` 技能负责管理

允许：

- 读取和检查项目根目录 `./onescience.json`
- 检测本地 `sbatch`
- 检测运行平台加速器类型：DCU/GPU；remote 时只能通过已验证 SSH Host 做有限检测
- 对 remote 配置做有限的 SSH/SCnet 连通性验证；SSH 私钥权限过宽时可自动修复并重试
- 读取 `assets/runsite.example.json` 和各类 profile
- 写入 `~/.ssh/config` 和 `~/.scnet-chat.env`
- 仅在 `onescience.json` 不存在时创建它
- 仅按用户明确要求修改已有 `onescience.json`
- 回传控制信息只出现在技能交接输出中，不写入 `onescience.json`

## 工具入口

```bash
python skills/onescience-runsite/scripts/runsite_config.py --config-path ./onescience.json check
python skills/onescience-runsite/scripts/runsite_config.py detect-local-slurm
python skills/onescience-runsite/scripts/runsite_config.py detect-hardware
python skills/onescience-runsite/scripts/runsite_config.py detect-hardware --ssh-alias <alias>
python skills/onescience-runsite/scripts/runsite_config.py --config-path ./onescience.json generate --run-site local --execution-mode none --accelerator-kind dcu
python skills/onescience-runsite/scripts/runsite_config.py --config-path ./onescience.json modify --field runtime.cluster.partition --value hpctest01
```

远程凭据保存：

```bash
python skills/onescience-runsite/scripts/ssh_config.py add --host <host> --port <port> --user <user> --identity <identity_file> --alias <alias>
python skills/onescience-runsite/scripts/ssh_config.py check --alias <alias>
python skills/onescience-runsite/scripts/scnet_config.py set --access-key <key> --secret-key <secret> --user <user> --region <region>
python skills/onescience-runsite/scripts/scnet_config.py check-login
```

远程生成时直接传 JSON 或环境变量，不创建临时 JSON 文件：

```bash
python skills/onescience-runsite/scripts/runsite_config.py --config-path ./onescience.json generate \
  --run-site remote \
  --execution-mode slurm \
  --access-mode ssh \
  --accelerator-kind dcu \
  --ssh-data '{"host":"cluster","hostname":"192.168.1.100","port":22,"user":"alice","identity_file":"~/.ssh/id_rsa","remote_work_dir":"/home/alice/work"}' \
  --cluster-data '{"partition":"hpctest01","nodes":1,"gpus_per_node":1,"cpus_per_task":8,"memory":"64GB","time_limit":"02:00:00","gpu_type":"dcu","ntasks_per_node":1}'
```

## 交接

完成发现、创建、复用或修改后，输出不含密钥明文的结构化交接：

```json
{
  "config_file": "./onescience.json",
  "config_exists": true,
  "execution_profile": {
    "run_site": "local|remote",
    "execution_mode": "slurm|null",
    "access_mode": "ssh|scnet|"
  },
  "hardware_detected": {
    "accelerator_kind": "dcu|gpu",
    "accelerator_vendor": "amd|nvidia",
    "cpu_arch": "x86_64|arm64"
  },
  "credential_source": "~/.ssh/config|~/.scnet-chat.env|null",
  "account_summary": {
    "ssh_host_alias": "name-or-null",
    "scnet_user": "name-or-null"
  },
  "cluster_config": {
    "scheduler_type": "slurm|null",
    "partition": "...",
    "resources": {}
  },
  "next_action": "onescience-runtime|onescience-installer|ask_user"
}
```

### 回传规则

- 如果 `onescience-runsite` 是被其它技能临时调用来补齐配置，完成后必须优先回到调用它的技能，让调用方重新读取 `./onescience.json` 并继续原任务。
- 调用方身份来自技能调用上下文，不要求脚本参数，也不写入 `onescience.json`。
- 如果没有明确调用方，或配置完成后无法判断应继续运行、安装、编码还是诊断，`next_action` 必须是 `onescience-orchestrator`，由 orchestrator 重新规划下一步。
- 只有远程连接验证失败、缺少必要用户信息或需要用户明确确认时，才把 `next_action` 设为 `ask_user`。
- 不要在完成配置后默认跳到 `onescience-runtime` 或 `onescience-installer`；除非它们就是调用方。

## 一句话原则

`onescience-runsite` 只做配置发现、补问、保存、复用和交接。新版入口是 `run_site + execution_mode + access_mode`，当
`run_site=local` 时 `access_mode` 必须为空。
