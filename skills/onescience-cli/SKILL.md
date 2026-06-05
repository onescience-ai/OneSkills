---
name: onescience-cli
description: 在远程 SSH/SLURM 环境中通过 `onescience` 命令执行任意 OneScience 子命令。根据命令级别（lightweight/normal/compute）自动选择执行通道。环境初始化由 `onescience-installer` 技能处理，计算节点申请与作业提交由 `onescience-runtime` 技能处理。本技能只负责 `onescience` 命令的调度与执行。
---

# OneScience CLI 技能

**本技能根目录：** 与当前 `SKILL.md` 同目录。资产路径均按本技能根目录解析，不按当前工作目录猜测。

需要环境检测与远程连接细则时，读取 `./references/cli_rules.md`。
需要可渲染命令模板时，读取 `./references/cli_flow.md`。

## 1. 职责与边界

本技能是在远端环境执行任意 `onescience` 命令的统一入口。`onescience` 命令需预先安装，本技能不检查或安装 `onescience` 工具。本技能不限制子命令范围，任何 `onescience` 支持的子命令均可透传执行。

**负责：**

- 执行 `discover -> precheck（先检查计算节点 → 再检查环境）-> execute` 运行闭环
- 根据命令级别（lightweight/normal/compute）自动选择执行通道
- 轻量命令（help/list/info/config）走快速通道，跳过环境探测与检查
- 消费 `execution_mode`、`access_mode`、`execution_channel`、`hardware_profile`
- 连接远端环境（参照 `onescience-installer` 的主机发现与连接方式）
- 环境检查：确认当前 shell 在计算节点上、环境已加载
- 调用 `onescience` 命令执行用户请求的子命令
- 返回执行结果与状态

**不负责：**

- 安装或修复 OneScience 完整环境（由 `onescience-installer` 负责）
- 安装或修复 `onescience` 工具
- 计算节点申请与 SLURM 作业提交（由 `onescience-runtime` 负责）
- 修改远端代码、配置或依赖
- 安装系统级组件或驱动
- 深度诊断训练/测试失败的业务原因

## 2. 固定阶段

| 阶段 | 触发条件 | 目标 | 关键输出 |
|------|----------|------|----------|
| `discover` | 每次执行 | 命令级别判定 + 连接远端环境，收集运行目标与环境事实 | `execution_mode`、`hardware_profile`、`remote_access_info`、`command_level` |
| `precheck` | 非 lightweight 级别 | 检查环境是否满足运行条件（先计算节点 → 再环境） | `env_ready`、`on_compute_node`、`precheck_outcome` |
| `execute` | precheck 通过或 lightweight 快速通道 | 通过 `onescience` 命令执行用户请求的子命令 | `onescience_command`、`execution_state`、`output` |

三阶段按顺序推进，每阶段向用户实时汇报当前步骤。`lightweight` 级别跳过 precheck 直接进入 execute 快速通道。

`precheck` 发现不在计算节点时，交由 `onescience-runtime` 通过 sbatch 提交作业处理。`precheck` 发现环境未加载时，提示调用 `onescience-installer`。

## 3. Discover 阶段

### 3.1 消费上游信息

优先消费：
- `skills/onescience-runtime/assets/execution_profiles.json`
- `skills/onescience-runtime/assets/backend_specs.json`
- 上游传递的 `hardware_profile`、`execution_mode`、`access_mode`

### 3.2 执行域判定

若上游未给出可靠 `execution_mode`，用 `cli_flow.md` 的 `§0` 判定当前 shell 是否已在目标环境中。

- `IN_CONTAINER=yes`：视为 `local_slurm`，当前 shell 即为执行目标
- `IN_CONTAINER=no`：视为 `remote_slurm`，必须先完成主机发现

### 3.2a 命令级别判定

根据 `cli_rules.md §0.1` 规则判定当前命令级别：

| 级别 | 包含命令 |
|------|---------|
| `lightweight` | help, --version, list, info, config show/get |
| `normal` | log, status, upgrade, remock, config set |
| `compute` | bench 及所有训练/推理/评估命令 |

- `lightweight` → 跳过 §1 环境探测和 §3 环境检查，走快速通道
- `normal` → 跳过 §1 环境探测和 §2 计算节点判定，执行 §3 环境检查
- `compute` → 执行完整三阶段

### 3.3 主机发现（remote_slurm）

参照 `onescience-installer` 的主机发现流程：

1. 读取 `onescience.json` 的 `runtime.remote`
2. 读取 `~/.ssh/config`
3. 仍缺 `user`、`host`/`hostname`、`port`、`identity_file` 中任一项时，只询问缺失项
4. 多个 Host 候选时，只询问选哪一个

**Host 别名优先**：当 `~/.ssh/config` 中存在配置完整的 Host 条目时，使用 `{ssh_host_alias}` 替代完整的 `-p -i user@host` 参数。

### 3.4 §1 远端环境探测（硬件探测）

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

**实时汇报**：`🔄 正在执行 §1 远端环境探测...`

## 4. Precheck 阶段

命令级别决定跳过哪些检查步骤：

| 级别 | §2 计算节点判定 | §3 环境加载检查 |
|------|----------------|----------------|
| `lightweight` | 跳过 | 跳过（走快速通道） |
| `normal` | 跳过 | 执行 |
| `compute` | 执行 | 执行 |

### 4.1 §2 计算节点判定（第一步）

**仅对 `compute` 级别执行**。

**执行命令**：
- `remote_slurm`：执行 `cli_flow.md` 的 `§2` 远端判定
- `local_slurm`：执行 `cli_flow.md` 的 `§2` 就地判定

**检查内容**：
- `SLURM_NODEID`：检查是否已设置
- `SLURM_JOB_ID`：检查是否已设置
- `SLURM_JOB_NODELIST`：检查是否已设置
- `SLURM_NTASKS`：检查是否已设置
- `SLURM_CLUSTER_NAME`：检查是否已设置
- `hostname`：获取当前主机名
- `scontrol show node`：尝试获取节点信息

**实时汇报**：`📋 正在执行 §2 计算节点判定...`

**不在计算节点时**：调用 `onescience-runtime` 技能，通过 sbatch 提交作业到计算节点执行。

---

### 4.2 §3 环境加载检查（第二步）

**对 `normal` 和 `compute` 级别执行**。

**执行命令**：
- `remote_slurm`：执行 `cli_flow.md` 的 `§3` 远端检查
- `local_slurm`：执行 `cli_flow.md` 的 `§3` 就地检查

**检查内容**：
- Conda 环境列表：检查 `onescience311` 是否存在
- 当前激活环境：检查 `$CONDA_DEFAULT_ENV` 是否为 `onescience311`
- 已加载模块：检查 `module list` 输出
- OneScience 包：检查 `python -c "import onescience; print(onescience.__version__)"` 是否成功

**实时汇报**：`📋 正在执行 §3 环境加载检查...`

**不满足条件时**：调用 `onescience-installer` 技能完成环境初始化。

## 5. Execute 阶段

### 5.1 onescience 命令

命令形式为：

```
onescience {onescience_subcommand} {onescience_args}
```

其中 `{onescience_subcommand}` 是用户请求的子命令，`{onescience_args}` 是子命令后的附加参数。

### 5.2 模板选择

根据命令级别和执行模式选择模板：

| 级别 | remote_slurm | local_slurm |
|------|-------------|-------------|
| lightweight | `§5` 快速执行通道 | `§5` 就地 |
| normal | `§6` 普通执行命令 | `§6` 就地 |
| compute | `§4` 通用执行命令 | `§7` 通用执行命令 |

**快速通道（lightweight）特点**：
- 跳过环境探测、计算节点判定、环境加载检查
- 直接执行 onescience 命令
- 无需设置 WORLD_SIZE/MASTER_ADDR/MASTER_PORT 等环境变量
- 无需切换工作目录

**普通通道（normal）特点**：
- 跳过环境探测和计算节点判定
- 已确认环境就绪，直接执行

**计算通道（compute）特点**：
- 完整三阶段流程
- 需要确认在计算节点上
- 需要设置完整的训练环境变量

### 5.3 执行方式

- `remote_slurm`：通过 SSH 在远端执行 `onescience` 命令
  - lightweight：直接在远端执行（登录节点即可）
  - normal：直接在远端执行（登录节点即可）
  - compute：需在计算节点上执行；不在时通过 `onescience-runtime` 的 sbatch 提交作业
- `local_slurm`：在当前计算节点上直接执行 `onescience` 命令

### 5.4 日志与输出管理

**日志路径**：
- 远端日志目录：`{remote_work_dir}/.onescience/cli_logs`
- 远端输出目录：`{remote_work_dir}/.onescience/output`

**日志同步**：
- `remote_slurm`：执行完成后通过 `scp` 同步日志到本地 `.onescience/cli_logs/`
- `local_slurm`：直接复制到本地 `.onescience/cli_logs/`

**输出展示**：
- 执行日志路径（远端 + 本地）
- 输出文件列表
- 关键指标（如训练 loss、准确率等）

## 6. 用户交互

只在以下情况询问用户：

- 主机发现后仍缺 SSH 四元组中的字段
- 多个 Host 候选需要择一
- 不在计算节点上（compute 级别），建议交由 `onescience-runtime` 通过 sbatch 提交作业
- 环境未加载（env_not_ready），建议调用 `onescience-installer`

## 7. 最终输出

每次阶段汇报或执行完成时，直接向用户展示以下内容，无需用户再次询问：

### 快速通道输出（lightweight 级别）

```
🚀 快速通道：跳过环境探测与检查，直接执行
📋 目标主机：{hostname}
📋 命令级别：lightweight

🚀 execute：正在执行 onescience {onescience_subcommand} {onescience_args}...
📊 输出结果：
{output}

📊 执行状态：{execution_state}
📊 退出码：{exit_code}
```

### 标准通道输出（normal / compute 级别）

```
🔄 discover：正在连接远端环境...
📋 目标主机：{hostname}
📋 硬件类型：{required_backend_id}
📋 执行模式：{execution_mode}

🔄 precheck：正在检查环境...
📋 计算节点状态：{on_compute_node}
📋 环境加载状态：{env_ready}

🚀 execute：正在执行 onescience {onescience_subcommand} {onescience_args}...
📊 输出结果：
{output}

📊 执行状态：{execution_state}
📊 退出码：{exit_code}
📂 日志路径：{log_path}
```

### 失败时输出错误诊断

```
❌ 执行失败
📋 错误类型：{error_category}
📋 错误信息：{error_message}
📋 建议：{suggested_action}
📊 退出码：{exit_code}
```

### 错误类型说明
| 错误类型 | 说明 |
|----------|------|
| `command_not_found` | onescience 命令未找到 |
| `permission_denied` | 权限不足 |
| `missing_config` | 配置文件缺失 |
| `missing_data` | 数据文件缺失 |
| `out_of_memory` | 内存不足 |
| `network_error` | 网络错误 |
| `cli_error` | onescience 命令执行错误 |
| `ssh_failure` | SSH 连接失败 |

## 8. 跨技能调用与验证

### 8.1 调用 onescience-installer 后的验证

**验证流程**：
1. 等待 `onescience-installer` 返回 `verify_state=verified`
2. 重新执行 §3 环境加载检查
3. 确认 `env_ready=true` 后才进入 execute
4. 若仍为 `false`，输出：
   ```
   ❌ 环境安装失败
   📋 建议：手动检查环境或联系管理员
   ```

### 8.2 调用 onescience-runtime 后的状态跟踪

**状态跟踪流程**：
1. 调用 runtime 提交 sbatch 作业
2. 记录 `job_id`
3. 使用 `squeue -j {job_id}` 轮询状态
4. 作业完成后：
   - 同步日志
   - 提取执行结果
   - 向用户展示

## 9. 参考文件

| 文件 | 用途 |
|------|------|
| `./references/cli_flow.md` | 可渲染命令模板（§0–§7） |
| `./references/cli_rules.md` | discover / precheck / execute 细则，含命令分级、快速通道和 Host Key 容错 |
| `skills/onescience-installer/SKILL.md` | 环境初始化委托给 `onescience-installer` 技能处理 |
| `skills/onescience-runtime/SKILL.md` | 计算节点申请与作业提交委托给 `onescience-runtime` 技能处理 |
