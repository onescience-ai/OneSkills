---
name: onescience-runsite
description: 解析、校验、保存和复用 OneScience 运行站点配置。用于任意技能在继续执行任务前补齐运行站点配置，完成配置发现、缺失字段补问、已有配置复用、remote 连接验证、运行平台 DCU/GPU 类型确认、modules 写入和结构化回传。当任务需要远端算力或特定软件（如 VASP/QE/CP2K）且存在多个 SSH 工作台连接时，必须对候选连接做只读软件环境探测，并通过 question 工具弹出工作台选择框、把拥有目标环境的连接标注（推荐）供用户确认。不做安装、不提交作业、不执行运行；仅允许连接验证、DCU/GPU 类型检测和有限的只读软件矩阵探测。
type: executor
capabilities:
  owns:
    - 运行站点配置解析
    - 校验
    - 保存
    - 复用
    - 缺失字段补问
    - 远程连接验证
    - 平台类型确认
    - modules写入
    - 多远程工作台选择
    - 远程软件环境只读探测
    - question工作台弹窗推荐
  not_owns:
    - 安装
    - 作业提交
    - 运行执行
  inputs:
    - onescience.json
    - user_input
  outputs:
    - onescience.json
    - runsite_handoff
  downstream: []
  prereq: []
  intent_aspects:
    - runsite_config
    - site_configuration
  operation_types:
    - create
    - adapt
  artifact_types:
    - config
  domains:
    - general
  trigger_keywords:
    - 运行站点
    - run_site
    - SSH配置
    - SLURM配置
    - 远程连接
    - 平台配置
    - 工作台选择
    - 多SSH连接
    - 环境探测
    - VASP
---

## 输入获取方式

本技能支持两种输入方式：

1. **上下文 handoff**（默认）：从调用方传入的 `step_handoff` 获取任务信息。
2. **文件 handoff**（autonomous_mode）：从 `.onescience/handoff/step_{step_id}.yaml`
   读取任务信息。执行后，将结果写入 `.onescience/handoff/step_{step_id}_result.yaml`。

启动时优先检查 `.onescience/handoff/` 目录是否存在对应的交接文件；若存在则使用文件模式，否则使用上下文模式。

文件交接格式参见 `skills/onescience-orchestrator/references/file_handoff_contract.md`。

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
| 创建远程配置，包含 SSH、SCnet 或 MCP        | `references/remote_runsite.md`        |

## 补问硬规则

### 预配置免交互（Autonomous Mode）

当上游 `step_handoff.execution_flags.autonomous_mode` 为 `true` 时：

1. 若 `onescience.json` 已存在且完整，直接验证并使用，不触发任何补问流程。
2. 若 `onescience.json` 缺失或不完整，按以下优先级自动处理：
   - 检测本地环境（GPU/CUDA、conda 等）是否可用 → 自动生成本地配置（`run_site=local`），不向用户提问。
   - 若本地不支持但存在 `.onescience/default_remote.json` 预配置文件 → 读取并使用。
   - 若必须使用远程环境但配置信息不完整 → 返回 `status: blocked` 并输出缺失字段清单（不进入逐字段补问流程）。
3. 禁止在 autonomous_mode 下向用户发起任何交互式提问。

### 标准补问规则（默认模式）

- 不允许只说“请提供 SSH 信息”“请提供 SCnet 信息”“请提供 cluster 信息”。
- 需要用户提供信息时，必须逐一列出字段名、含义、是否可留空或默认值。
- 可以逐字段一问一答，也可以给出一个字段清单让用户一次性填写；但字段清单必须完整。
- 远程接入方式按优先级自动判定，不无条件要求 SSH：
  1. `~/.ssh/config` 中平台连接 ≥ 2 个（`# >>> opencode ssh` 块）→ 触发下文“多远程工作台选择”弹窗；弹窗只列各 SSH 连接本身（含预置连接与用户自加连接），**不插入“平台默认（SCNet MCP 优先）”这类合成选项，也不在选项里描述 MCP/SSH 连接方式**。用户选中某连接后由 runsite 内部定接入方式（弹窗不体现）：选中的若是**平台预置 SCNet 连接**（SCNet MCP 所对应、由平台注入的默认那条）→ `access_mode=mcp` 并**同时写该连接 `runtime.ssh` 作运行期回退**；其余连接 → `access_mode=ssh` 写 `runtime.ssh`。无法判定是否预置时按 `ssh` 处理（用所选连接本身，最稳妥）。
  2. 平台连接 ≤ 1 个且任务本地不满足 → 不弹框，默认 `access_mode=mcp`（运行期先试 SCNet MCP，调不通回退读 `~/.ssh/config` 走该连接 SSH）。
  3. 完全没有可用连接、需用户首次提供凭据时 → 才进入逐字段补问。
- 接入方式确定后，只补问该方式需要的字段：
  - `access_mode=ssh`：补问并验证 SSH 连接字段。
  - `access_mode=scnet`：补问并验证 SCnet 凭据字段；不再强制补问 SSH。
  - `access_mode=mcp`：无需任何凭据字段（凭据由平台托管），既不补问 SSH也不补问 SCnet。
- 连接信息完成后，才询问是否使用 Slurm；只有用户明确选择使用 Slurm 后，才补问 Slurm 集群资源字段。
- 已有 `onescience.json` 不完整时，必须先根据 `run_site`、`execution_mode`、`access_mode` 判断哪些配置块是必填，再只补问这些必填块中缺失的字段；补问时仍必须列出每个缺失字段。
- 远程连接验证失败后，要求用户重新提交信息时，也必须列出对应接入方式需要重新提供的字段。
- SSH 字段（`host`/别名、`hostname`、`port`、`user`、`identity_file`、`remote_work_dir`）在 `access_mode=ssh` 时校验并补齐；`access_mode=mcp` 不强制要求 SSH，但经弹窗选中的预置连接会**同时写入其 `runtime.ssh` 作为运行期回退**（无 `runtime.ssh` 时回退改从 `~/.ssh/config` 现取）。
- SCnet 字段（`SCNET_ACCESS_KEY`、`SCNET_SECRET_KEY`、`SCNET_USER`、`region`、`remote_work_dir`）仅在 `access_mode=scnet` 时校验并补齐。
- 只要 `execution_mode=slurm`，都必须校验并补齐 Slurm 字段：`partition`、`nodes`、`gpus_per_node`、`cpus_per_task`、`memory`、`time_limit`、`gpu_type`、`ntasks_per_node`。
- 用户提供完整运行信息后，必须检测对应运行平台加速器类型：本地直接/本地 Slurm 检测本机；远程 SSH 直接/远程 SSH Slurm 通过已验证 SSH Host 别名检测远程。若未检测出，先询问用户确认 `dcu` 还是 `gpu`，再生成配置。

### 多远程工作台选择与推荐（question 弹窗硬规则）

适用条件（同时满足即必须触发，不得跳过、不得替用户自行决定）：

1. 当前任务需要远端算力或特定软件环境（如 VASP、QE、CP2K 等第一性原理/商软，或大规模 MD/训练），本地不具备；**且**
2. `~/.ssh/config` 中存在 **2 个及以上** 可选的平台 SSH 连接（`# >>> opencode ssh <name>` 块，含预置连接与用户自加连接）——需要让用户在多个执行环境之间选择具体在哪一台上执行；连接方式（MCP/SSH）是实现细节，不在弹窗中呈现。

> **连接数 ≤ 1（未自加 SSH）时不弹框**：默认走 `access_mode=mcp`（平台优先），直接进入下文“单连接/零连接”流程，不触发本弹窗。

> **强制覆盖 autonomous_mode**：本工作台选择弹窗是面向用户的执行位置决策（涉及商软许可证、账号归属），**即使上游 `step_handoff.execution_flags.autonomous_mode` 为 `true` 也必须触发**，不受上文“autonomous_mode 禁止交互式提问”限制；此处应把 `next_action` 置为 `ask_user` 并调用 `question`，不得静默选定连接。

命中后必须按顺序执行：

1. 从任务上下文解析软件需求清单 `needs`（小写，逗号分隔，如 `vasp,lammps`）。
2. 运行 `python3 skills/onescience-runsite/scripts/probe_remote_env.py list-connections` 枚举候选连接。
3. 运行 `python3 skills/onescience-runsite/scripts/probe_remote_env.py probe --needs <needs> --cache ./onescience.probe_cache.json`，对每个连接做**只读**探测（`command -v`/`module avail`/加速器列表），得到 `connections[]`、`recommended`、每个连接 `reason`、`reachable`。
4. **必须且只能调用一次 `question` 工具**，且该弹窗**只包含“工作台连接选择”这一个问题**，规则：
   - `header` 固定为 `工作台环境`；`question` 用中文说明当前任务需要哪类环境（如“MOF-5 第一性原理参考计算需要 VASP，请选择执行该任务的工作台环境”）。
   - `options` **只列 probe 返回的各个候选 SSH 连接**（含预置连接与用户自加连接），**不得插入“平台默认（SCNet MCP 优先）”之类的合成选项，也不得在 `description` 里描述 MCP/SSH 连接方式**：每个连接一项，`label` 为连接名，`description` 写入探测依据（命中的软件、加速器、连通状态、`reason`）。选中某连接后，`access_mode` 由 runsite 依“是否平台预置 SCNet 连接”内部判定（预置→`mcp` 且写 `runtime.ssh` 回退、其余→`ssh`），弹窗选项文本不体现该判定。
   - `options` 顺序直接沿用 probe 返回的 `connections[]`（probe 已按 `recommendable`→`score` 降序排好）。**仅当顶层 `recommended` 非空时**，才在该连接 `label` 末尾追加 `（推荐）`；**`recommended` 为空（含 `null`）时不得给任何连接追加 `（推荐）`，严禁退而选 `score` 最高或“可达但无商软”的连接当推荐**。当 `probe_incomplete=true` 或某连接 `unverified=true` 时，在该连接 `description` 如实标注“探测超时/未验证，需重试”（不得等同于不可达），将其排在列表前列供用户注意，并在 question 正文提示“存在未完成验证的候选（如 xsl），建议重试探测或据此手动选择”，但**不标（推荐）**。无论是否探到，都不得省略弹窗。
   - `multiple=false`；**不得在同一个 question 里再塞入“工作目录 / 是否用 Slurm / 加速器类型 / 分区”等其它问题**——这些字段由下一步自动推导，不向用户提问。
5. 用户选定连接后，**其余远程字段一律自动确定、不得再弹任何 question**：
   - `remote_work_dir`：取探测返回的远端家目录（`echo $HOME`）；缺省用 `/public/home/<user>` 或用户家目录，直接写入不追问。
   - `execution_mode`：探测到 `sbatch`/SBATCH 即置 `slurm`，否则置 `null`（直连），不追问。
   - `partition`：优先取探测到的默认分区（`sinfo`/`scontrol` 或 config 注释）；探不到则留空并在正文标注为待下游补全，不追问。
   - `accelerator_kind`：探测到 `dtk`/DCU 置 `dcu`，`nvidia-smi` 置 `gpu`；都探不到时按模块线索推断（含 `dtk`→`dcu`），仍无法判定则默认 `dcu` 并在正文标注假设，不向用户提问。
   - 写回 `onescience.json`：用户选 **某个连接** → `run_site=remote`，一律用该连接 SSH 参数 + 上述自动值写 `runtime.ssh`、`runtime.cluster`、`runtime.target`；`access_mode` 取 `mcp`（选中项为平台预置 SCNet 连接时，MCP 优先、`runtime.ssh` 兜底）或 `ssh`（其余连接）。
6. 仅 1 个连接、或任务本地即可满足时，不触发该弹窗；**远程且连接数 ≤ 1 时默认 `access_mode=mcp`（平台优先，运行期先试 SCNet MCP、调不通回退 SSH），不写 `runtime.ssh`**。此时同样**不得**为工作目录/Slurm/加速器逐字段弹问，全部按第 5 步自动推导。

> **唯一交互点原则**：runsite 面向用户的交互式弹窗**有且只有“工作台连接选择”这一个**。`remote_work_dir`、`execution_mode`、`partition`、`accelerator_kind` 等运行细节即便无法自动确定，也只能写入配置或用默认值落地并在正文标注假设，**严禁再用 question 逐字段追问用户**。下文“标准补问规则”仅在 `~/.ssh/config` 中完全没有可用连接、必须让用户首次提供 SSH 凭据时才生效；一旦存在 ≥1 个已配置连接，即按本节单弹窗流程处理，不进入逐字段补问。

探测与弹窗边界：只做只读探测，不安装、不提交作业；私钥只按 `~/.ssh/config` 中的路径引用，脚本与 `question` 选项文本**一律不得读取或展示密钥内容**；连接不可达或探测失败必须在对应 `description` 中如实标注。**超时/连接失败而 `unverified=true` 的连接属“未验证”，不得表述为“不可达”，也不得因此把它排除出候选或把不满足需求的连接改标为推荐。**

有脚本时优先用 `scripts/runsite_config.py`、`scripts/ssh_config.py`、`scripts/scnet_config.py`、`scripts/probe_remote_env.py`。

## 字段所有权

`onescience-runsite` 只负责以下 `onescience.json` 字段的创建和更新：

**必须管理的字段：**
- `runtime.execution_profile`（`run_site`、`execution_mode`、`access_mode`）
- `runtime.ssh`（当 `run_site=remote` 且 `access_mode=ssh` 时）
- `runtime.scnet`（当 `access_mode=scnet` 时）；`access_mode=mcp` 时两者均不写，凭据由平台托管
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
  "access_mode": "ssh|scnet|mcp|"
}
```

规则：

- `run_site` 只能是 `local` 或 `remote`。
- `execution_mode` 只能是 `slurm` 或  `null`。
- `access_mode` 只能是 `ssh`、`scnet` 或 `mcp`；当 `run_site=local` 时必须为空字符串 `""`。`mcp` 表示平台优先（运行期先试 SCNet MCP，调不通回退 SSH）。
- 不再生成或依赖 `execution_channel`。
- 不再把 `remote_slurm`、`remote_direct`、`cloud_api` 这些旧值写入新配置。

## 硬边界

禁止：

- 安装环境：`conda create`、`pip install`、`git clone`、`bash install.sh`
- 提交或运行作业：`sbatch`、`srun`、训练脚本、推理脚本
- 除“连接验证、有限 DCU/GPU 类型检测、以及多远程工作台选择下的只读软件矩阵探测（`scripts/probe_remote_env.py`）”外做远端就绪探测：远端 `sbatch`、`squeue`、`sacct`、远端可写性检查、安装性探测
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
- 多远程工作台选择时，通过 `scripts/probe_remote_env.py` 对各 SSH 连接做只读软件矩阵/加速器探测，并调用 `question` 工具弹出工作台选择框（推荐项标（推荐））

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
    "access_mode": "ssh|scnet|mcp|"
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
- `next_action` 表示“回 caller 或回 orchestrator”的上下文字段，不是默认跳转目标；runsite 不得自行推断新的业务 downstream skill。
- 如果没有明确调用方，或配置完成后无法判断应继续运行、安装、编码还是诊断，`next_action` 必须是 `onescience-orchestrator`，由 orchestrator 重新规划下一步。
- 只有远程连接验证失败、缺少必要用户信息或需要用户明确确认时，才把 `next_action` 设为 `ask_user`。
- 不要在完成配置后默认跳到 `onescience-runtime` 或 `onescience-installer`；除非它们就是调用方。

## 一句话原则

`onescience-runsite` 只做配置发现、补问、保存、复用和交接。新版入口是 `run_site + execution_mode + access_mode`，当
`run_site=local` 时 `access_mode` 必须为空。
