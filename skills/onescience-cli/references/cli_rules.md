# CLI Rules — 流程细则

本文件承载 `discover / precheck / execute` 的详细裁决规则。环境初始化由 `onescience-installer` 技能处理，计算节点申请与作业提交由 `onescience-runtime` 技能处理。本技能只负责 `onescience` 命令的执行。门禁与阶段轮廓见 `../SKILL.md`；可渲染命令模板见 `./cli_flow.md`。

## 目录

- [§0 命令分级与快速通道](#0-命令分级与快速通道)
- [§1 Discover 细则](#1-discover-细则)
- [§2 Precheck 规则](#2-precheck-规则)
- [§3 Execute 规则](#3-execute-规则)
- [§4 用户交互规则](#4-用户交互规则)
- [§5 失败处理](#5-失败处理)

---

## §0 命令分级与快速通道

### §0.1 命令分级

根据命令类型和资源需求，将 onescience 子命令分为三级：

| 级别 | 包含命令 | 判定条件 |
|------|---------|----------|
| `lightweight` | `help`, `--version` | 用户请求的子命令为 help 或 --version |
| | `list`, `info`, `config`（不含子命令或 show/get） | 用户请求的子命令在列表中 |
| `normal` | `log`, `status`, `upgrade`, `remock` | 用户请求的子命令在列表中 |
| | `config set`, `config`（其他子命令） | |
| `compute` | `bench` 及所有训练/推理/评估命令 | 以上全部不符合时默认为 compute |

**判定逻辑**：
1. 提取用户请求中的 `{onescience_subcommand}`
2. 与分级表逐级匹配
3. 若无法判定，默认按 `compute` 级别处理

### §0.2 快速执行通道

当满足以下**全部**条件时，激活快速执行通道，跳过环境探测和检查：

1. 命令级别判定为 `lightweight`
2. `~/.ssh/config` 中已存在配置完整的 Host 条目（user/hostname/port/identity_file 均已配置）
3. 没有上游传入的 `hardware_profile` 或 `execution_mode` 要求必须进行完整检查

**快速通道流程**：
- discover 阶段：只做主机发现，**跳过 §1 远端环境探测**
- precheck 阶段：**跳过 §2 计算节点判定** 和 **§3 环境加载检查**
- execute 阶段：直接执行 `cli_flow.md` 的 `§5` 快速执行通道模板

**实时汇报**：`🚀 快速通道：跳过环境探测与检查，直接执行`

### §0.3 SSH Host Key 容错

**规则**：
- 所有通过 SSH 执行的命令，默认追加 SSH 选项：
  - `-o StrictHostKeyChecking=no`
  - `-o UserKnownHostsFile=/dev/null`
- 当 `~/.ssh/config` 的 Host 条目中已配置 `StrictHostKeyChecking no` 时，同样追加 `UserKnownHostsFile=/dev/null`

**Host 别名优先**：
- 当 `~/.ssh/config` 中存在配置完整的 Host 条目（user/hostname/port/identity_file 齐全）时，**优先使用 Host 别名** `{ssh_host_alias}` 替代完整的 `-p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server}`
- Host 别名携带了所有 SSH 参数，避免在命令行手动拼接，同时减少 PowerShell 引号解析问题

**实时汇报**：`📋 SSH Host Key 容错：使用 UserKnownHostsFile=/dev/null`

---

## 1. Discover 细则

### 1.1 优先消费的上游信息

- `skills/onescience-runtime/assets/execution_profiles.json`
- `skills/onescience-runtime/assets/backend_specs.json`
- 上游传递的 `hardware_profile`、`execution_mode`、`access_mode`
- 用户请求中的 onescience 子命令与参数

### 1.2 执行域判定

若上游未给出可靠 `execution_profile`，用 `cli_flow.md` 的 `§0` 判定当前 shell 是否已在目标环境中：

- `IN_CONTAINER=yes`：视为 `local_slurm`，当前 shell 就是执行目标，禁止再 `ssh`
- `IN_CONTAINER=no`：视为 `remote_slurm`，必须先完成主机发现

### 1.2a 命令级别判定

根据 §0.1 规则判定当前命令级别：

- `lightweight` → 跳过 §1.4 远端环境探测，直接进入快速通道
- `normal` → 跳过 §1.4 远端环境探测，跳转到 precheck §3
- `compute` → 继续执行 §1.4 远端环境探测

### 1.3 主机发现（remote_slurm）

顺序：

1. 读取 `onescience.json` 的 `runtime.remote`
2. 读取 `~/.ssh/config`
3. 仍缺 `user`、`host`/`hostname`、`port`、`identity_file` 中任一项时，只询问缺失项
4. 多个 Host 候选时，只询问选哪一个

`{ssh_server}` 优先 `hostname`，否则 `host`。

**Host 别名优先**：当 `~/.ssh/config` 中存在配置完整的 Host 条目时，使用 `{ssh_host_alias}` 替代完整的 `-p {ssh_port} -i {ssh_identity} {ssh_user}@{ssh_server}`。所有后续 SSH 命令均使用此别名。

**Host Key 容错**：发现 Host 已配置 `StrictHostKeyChecking no` 时，自动追加 `-o UserKnownHostsFile=/dev/null`。

### 1.4 §1 远端环境探测（硬件探测）

**仅对 `compute` 级别执行**：`lightweight` 和 `normal` 级别跳过本节。

**执行命令**：
- `remote_slurm`：执行 `cli_flow.md` 的 `§1`
- `local_slurm`：执行 `cli_flow.md` 的 `§1b`

**探测内容**：
- NVIDIA GPU 检测（`nvidia-smi`）
- AMD DCU 检测（`hipcc`）
- 工具包目录检测（`/opt/dtk-*`、`/opt/rocm*`、`/usr/local/cuda*`）
- 设备文件检测（`/dev/kfd`）
- 模块环境检测（`module avail`）

**生成 `required_backend_id`**：

| 优先级 | 探测信号 | `required_backend_id` |
|--------|----------|-----------------------|
| 1 | `module avail` 输出含 `dtk` 或 `sghpc` | `slurm_dcu` |
| 2 | `hipcc` 可用，或存在 `/opt/dtk-*` | `slurm_dcu` |
| 3 | `nvidia-smi` 有 GPU 且 `/usr/local/cuda*` 存在 | `slurm_gpu` |
| 4 | 以上皆不满足 | `slurm_cpu` |

**实时汇报**：`🔄 正在执行 §1 远端环境探测...`

---

## 2. Precheck 规则

`precheck` 按以下顺序执行检查步骤，并根据命令级别决定跳过哪些步骤：

### §2.0 命令分级跳过规则

| 命令级别 | §2.1 计算节点判定 | §2.2 环境加载检查 |
|---------|------------------|------------------|
| `lightweight` | **跳过** | **跳过** |
| `normal` | **跳过** | **执行** |
| `compute` | **执行** | **执行** |

### 2.1 §2 计算节点判定（第一步）

**仅对 `compute` 级别执行**：`lightweight` 和 `normal` 级别跳过本节。

**必须执行**：检查当前 shell 是否在计算节点上运行，训练/测试任务必须在计算节点上执行。

**执行命令**：
- `remote_slurm`：执行 `cli_flow.md` 的 `§2` 远端判定
- `local_slurm`：执行 `cli_flow.md` 的 `§2` 就地判定

**检查内容**：
- `SLURM_NODEID`：检查是否已设置（非 `not_set`）
- `SLURM_JOB_ID`：检查是否已设置（非 `not_set`）
- `SLURM_JOB_NODELIST`：检查是否已设置（非 `not_set`）
- `SLURM_NTASKS`：检查是否已设置（非 `not_set`）
- `SLURM_CLUSTER_NAME`：检查是否已设置（非 `not_set`）
- `hostname`：获取当前主机名
- `scontrol show node`：尝试获取节点信息

**结果语义**：

| 检查项 | 通过条件 | `on_compute_node` |
|--------|----------|-------------------|
| SLURM_NODEID | 已设置（非 `not_set`） | `true` |
| SLURM_JOB_ID | 已设置（非 `not_set`） | `true` |
| 登录节点特征 | hostname 匹配登录节点模式 | `false` |

**实时汇报**：`📋 正在执行 §2 计算节点判定...`

**不满足条件时**：
- 若 `on_compute_node=false`，当前 shell 在登录节点上
- **调用 `onescience-runtime` 技能**，通过 sbatch 提交作业到计算节点执行
- 本技能对登录节点不做任何 salloc/srun 处理

---

### 2.2 §3 环境加载检查（第二步）

**仅对 `normal` 和 `compute` 级别执行**：`lightweight` 级别跳过本节。

**必须执行**：检查 OneScience 环境是否已正确加载就绪。

**执行命令**：
- `remote_slurm`：执行 `cli_flow.md` 的 `§3` 远端检查
- `local_slurm`：执行 `cli_flow.md` 的 `§3` 就地检查

**检查内容**：
- Conda 环境列表：检查 `{env_name}`（默认 `onescience311`）是否存在
- 当前激活环境：检查 `$CONDA_DEFAULT_ENV` 是否为 `{env_name}`
- 已加载模块：检查 `module list` 输出
- OneScience 包：检查 `python -c "import onescience; print(onescience.__version__)"` 是否成功

**结果语义**：

| 检查项 | 通过条件 | `env_ready` |
|--------|----------|-------------|
| Conda 环境 | `conda info --envs` 包含 `{env_name}` | `true` / `false` |
| Conda 激活 | `$CONDA_DEFAULT_ENV` 等于 `{env_name}` | `true` / `false` |
| Module 环境 | 对应的 module 已在列表内 | `true` / `false` |
| OneScience 包 | `python -c "import onescience"` 成功 | `true` / `false` |

**实时汇报**：`📋 正在执行 §3 环境加载检查...`

**不满足条件时**：
- 若 `env_ready=false` 且 `on_compute_node=true`，输出 `blocking_reason=env_not_ready`
- **调用 `onescience-installer` 技能**完成环境初始化
- 初始化完成后再重新执行本技能

---

### 2.3 综合判定

| `on_compute_node` | `env_ready` | `precheck_outcome` | 后续动作 |
|-------------------|-------------|-------------------|----------|
| true | true | `ready_to_execute` | 直接进入 execute |
| false | — | `login_needed` | **调用 `onescience-runtime` 通过 sbatch 提交作业到计算节点执行** |
| true | false | `env_not_ready` | **调用 `onescience-installer` 完成环境初始化** |
| lightweight 跳过 | 跳过 | `quick_channel` | **直接进入 execute 快速通道** |
| normal 跳过计算节点 | true | `ready_to_execute` | **直接进入 execute 普通通道** |

---

## 3. Execute 规则

只有 `precheck_outcome=ready_to_execute` 或 `precheck_outcome=quick_channel` 才能进入 `execute`。

### 3.1 命令渲染约束

- 命令模板只从 `./cli_flow.md` 取
- 所有占位符必须先由 profile 或用户输入解析完成
- `remote_slurm` 的探测、执行各自只执行一次 SSH 命令
- `local_slurm` 不包 `ssh`
- 不能把多个 onescience 子命令的执行命令混在一起
- 命令级别决定使用的模板：
  - `lightweight` 级别使用 `§5` 快速执行通道模板
  - `normal` 级别使用 `§6` 普通执行模板
  - `compute` 级别使用 `§4`（远端）或 `§7`（就地）模板
- 仅在当前 shell 在计算节点上时直接执行；在登录节点时通过 `onescience-runtime` 的 sbatch 机制执行
- 执行前仅做 `source ~/.bashrc` 确保 PATH 正确，不做 env.sh / module / conda 加载
- 执行完成后返回完整输出（stdout + stderr），不截断
- 每执行一步向用户实时汇报当前步骤和状态

### 3.2 渲染来源

| 占位符 | 来源 |
|--------|------|
| `{ssh_host_alias}` | 来自 `~/.ssh/config` 的 Host 条目（优先使用） |
| `{ssh_port}`、`{ssh_identity}`、`{ssh_user}`、`{ssh_server}` | 来自 `onescience.json` 的 `runtime.remote` 或 `~/.ssh/config` |
| `{ssh_options}` | 读取 `onescience.json` 的 `runtime.remote.strict_host_key_checking`，并追加 `-o UserKnownHostsFile=/dev/null` |
| `{onescience_subcommand}` | 用户请求的 onescience 子命令 |
| `{onescience_args}` | onescience 子命令后的附加参数 |
| `{env_name}` | conda 环境名，用于环境检查（默认 `onescience311`） |
| `{remote_work_dir}` | 来自 `onescience.json` 的 `runtime.remote.remote_work_dir`。**必须指向包含 `setup.py` 和 `examples/` 目录的项目根目录**，如 `/public/home/zongwei/onescience`，默认 `/public/home/{ssh_user}` |
| `{onescience_datasets_dir}` | 来自 `onescience.json` 的 `runtime.script.env_vars.ONESCIENCE_DATASETS_DIR` |
| `{onescience_models_dir}` | 来自 `onescience.json` 的 `runtime.script.env_vars.ONESCIENCE_MODELS_DIR` |

### 3.3 模板章节选择

| `execution_mode` | 命令级别 | 探测 | 计算节点 | 环境检查 | 执行 |
|------------------|---------|------|----------|----------|------|
| `remote_slurm` | lightweight | 跳过 | 跳过 | 跳过 | `§5` |
| `remote_slurm` | normal | 跳过 | 跳过 | `§3` 远端 | `§6` |
| `remote_slurm` | compute | `§1` | `§2` 远端 | `§3` 远端 | `§4` |
| `local_slurm` | lightweight | 跳过 | 跳过 | 跳过 | `§5` |
| `local_slurm` | normal | 跳过 | 跳过 | `§3` 就地 | `§6` |
| `local_slurm` | compute | `§1b` | `§2` 就地 | `§3` 就地 | `§7` |

### 3.4 参数传递

`onescience` 命令的完整形式为 `onescience {onescience_subcommand} {onescience_args}`，所有配置参数由 onescience 工具内部读取配置文件处理，本技能不做任何注入。

```
onescience {onescience_subcommand} {onescience_args}
```

### 3.5 环境变量传递

**执行 onescience 命令前，必须设置以下环境变量**：

| 环境变量 | 来源 | 用途 |
|----------|------|------|
| `ONESCIENCE_DATASETS_DIR` | `onescience.json` 的 `runtime.script.env_vars.ONESCIENCE_DATASETS_DIR` | 数据集目录 |
| `ONESCIENCE_MODELS_DIR` | `onescience.json` 的 `runtime.script.env_vars.ONESCIENCE_MODELS_DIR` | 模型目录 |
| `WORLD_SIZE` | `onescience.json` 的 `runtime.script.env_vars.WORLD_SIZE` | 分布式训练进程数 |
| `MASTER_ADDR` | `onescience.json` 的 `runtime.script.env_vars.MASTER_ADDR` | 主节点地址 |
| `MASTER_PORT` | `onescience.json` 的 `runtime.script.env_vars.MASTER_PORT` | 主节点端口 |

**说明**：`lightweight` 和 `normal` 级别命令无需设置环境变量（只读/查询类命令）。

### 3.6 工作目录切换

**所有级别命令执行前都必须切换到正确的项目工作目录**，确保 CLI 代码的 `_find_project_root()` 能正确识别项目根目录（查找 `setup.py` 和 `examples/`）。

```bash
cd {remote_work_dir}
```

其中 `{remote_work_dir}` 优先级：
1. `onescience.json` 的 `runtime.remote.remote_work_dir`
2. 默认值 `/public/home/{ssh_user}`

**重要**：`remote_work_dir` 必须指向包含 `setup.py` 和 `examples/` 目录的项目根目录（如 `/public/home/zongwei/onescience`），而非用户主目录。

### 3.7 结果收集

执行完成后收集完整输出，不截断：

| 信息 | 来源 |
|------|------|
| `execution_state` | `success` / `failed` / `running` |
| `output` | onescience 命令的完整输出（stdout + stderr） |
| `exit_code` | 命令退出码 |
| `next_action` | 成功时返回 `completed`；失败时建议 `onescience-runtime` 做 diagnose |

#### 执行步骤汇报

执行过程中按以下步骤向用户实时汇报：

| 步骤 | 汇报内容 |
|------|----------|
| 0 | `🚀 快速通道：跳过环境探测与检查，直接执行`（仅 lightweight） |
| 1 | `🔄 discover：正在连接远端环境...` |
| 2 | `🔄 precheck：正在检查环境...` |
| 2a | `📋 检查计算节点状态...` |
| 2b | `📋 检查环境加载状态...` |
| 3 | `🚀 execute：正在执行 onescience {onescience_subcommand}...` |
| 4 | `📊 输出结果：` （完整输出） |
| 5 | 若遇到问题：`❌ 问题：{问题描述}` |

---

## 4. 用户交互规则

只在以下情况询问用户：

- `remote_slurm` 主机发现后仍缺 SSH 四元组中的字段
- `~/.ssh/config` 或配置文件给出多个 Host，必须择一
- 不在计算节点上（compute 级别），建议交由 `onescience-runtime` 通过 sbatch 提交作业
- 环境未加载（env_not_ready），建议调用 `onescience-installer` 完成环境初始化

其余情况应通过执行命令和汇报阶段状态推进。

---

## 5. 失败处理与诊断

### 5.1 错误分类

| 错误类型 | 判定方式 | 处理建议 |
|----------|----------|----------|
| `command_not_found` | 退出码 127，输出含 "command not found" | 检查 onescience 是否安装，建议调用 onescience-installer |
| `permission_denied` | 退出码 126 或输出含 "Permission denied" | 检查文件权限或联系管理员 |
| `missing_config` | 输出含 "config file not found" | 检查配置文件路径 |
| `missing_data` | 输出含 "file not found" 或 "data not found" | 检查数据文件路径或配置数据集目录 |
| `out_of_memory` | 输出含 "CUDA out of memory"、"HIP out of memory" 或 "Killed" | 建议减少 batch_size 或增加内存 |
| `network_error` | 输出含 "Connection timeout" 或 "Network error" | 检查网络连接 |
| `cli_error` | onescience 命令返回非零退出码（非上述类型） | 查看 onescience 错误日志 |
| `ssh_failure` | SSH 连接失败或认证失败 | 检查 SSH 配置或密钥 |
| `host_key_changed` | 输出含 "REMOTE HOST IDENTIFICATION HAS CHANGED" | 自动清理已知主机密钥并重试 |

### 5.2 诊断流程

1. 检查退出码
2. 分析 stderr 输出
3. 提取关键错误信息
4. 匹配错误分类
5. 给出处理建议

### 5.3 结构化错误输出

失败时返回：

```json
{
  "execution_state": "failed",
  "error_category": "missing_data",
  "exit_code": 1,
  "error_message": "file not found: /path/to/data.nc",
  "suggested_action": "检查数据文件路径是否正确，或调用 onescience-installer 配置数据目录",
  "output": "完整的命令输出..."
}
```

### 5.4 调用 onescience-installer 后的验证

**验证流程**：

1. 等待 `onescience-installer` 返回 `verify_state=verified`
2. 重新执行 §3 环境加载检查
3. 确认 `env_ready=true` 后才进入 execute
4. 若仍为 `false`，输出：
   ```
   ❌ 环境安装失败
   📋 建议：手动检查环境或联系管理员
   ```

### 5.5 调用 onescience-runtime 后的状态跟踪

**状态跟踪流程**：

1. 调用 runtime 提交 sbatch 作业
2. 记录 `job_id`
3. 使用 `squeue -j {job_id}` 轮询状态
4. 作业完成后：
   - 同步日志
   - 提取执行结果
   - 向用户展示

### 5.6 失败处理矩阵

| 失败点 | 处理 |
|--------|------|
| SSH 超时或认证失败 | 重试一次；仍失败则 `blocked` |
| Host Key 冲突 | 自动执行 `ssh-keygen -R` 清理后重试，仍失败则 `blocked` |
| 缺 SSH 字段且用户补齐后仍不完整 | `blocked`，列出缺失字段 |
| 不在计算节点上（compute 级别） | `precheck_outcome=login_needed`，交由 `onescience-runtime` 通过 sbatch 提交作业 |
| 环境未加载（已在计算节点） | `precheck_outcome=env_not_ready`，提示调用 `onescience-installer` 完成环境初始化 |
| onescience 命令执行失败 | 根据错误分类返回结构化错误信息 |
