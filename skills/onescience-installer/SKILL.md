---
name: onescience-installer
description: 在远程 SSH/SLURM 或已进入目标容器/登录节点的环境中安装、修复并验证 OneScience。内部固定执行 discover -> precheck -> install -> verify，消费 execution_profile、hardware_profile、install profile、workspace bootstrap profile 与 install domain profile；用户要求安装 earth/cfd/bio/matchem/all 等环境时使用。
type: executor
---

# OneScience Installer

**本技能根目录：** 与当前 `SKILL.md` 同目录。资产路径均按本技能根目录解析，不按当前工作目录猜测。

需要渲染安装/探测/验证命令时，读取 `./references/install_flow.md`。
需要 discover / precheck / install / verify 细则、占位符渲染与失败语义时，读取 `./references/install_rules.md`。  
需要阶段结构化示例时，读取 `./assets/phase_examples/`。  
需要安装请求 resolution 示例时，读取 `./assets/resolution_examples/`。

## 1. 职责与边界

本技能是 OneScience 的唯一公开安装/修复入口，目标是把指定运行环境推进到“可交回 `onescience-runtime` 继续运行验证”的状态。

**负责：**

- 执行 `discover -> precheck -> install -> verify` 四阶段安装闭环
- 消费并补齐 `execution_mode`、`access_mode`、`execution_channel`、`required_backend_id`、`hardware_profile`
- 根据 `backend_specs.json`、`execution_profiles.json` 和本技能资产解析 installer backend、workspace bootstrap profile、install domain profile
- 只做 user-space 安装：创建/复用 Conda 环境、获取 OneScience 仓库、执行 `bash install.sh`
- 用独立 verify 命令确认 `torch` 与 `onescience` 包可见，并产出结构化安装状态

**不负责：**

- 安装或升级内核态驱动、系统级 CUDA/ROCm、root 权限组件
- 修改远端 `setup.py`、`requirements.txt`、`constraints.txt` 来绕过安装失败
- 提交 `sbatch`、训练、推理、日志轮询或 runtime diagnose
- 在 `precheck` 已阻断时继续执行安装命令
- 把 `install_profile_ref` 当成 installer backend 名称；真正 backend 必须由 profile 绑定到 `./assets/backend_profiles.json`

安装成功不等于运行成功。只有 `verify` 通过时，`next_action` 才能指向 `onescience-runtime`。

## 2. 固定阶段

| 阶段 | 目标 | 关键输出 |
|------|------|----------|
| `discover` | 收集安装目标与环境事实 | `execution_mode`、`required_backend_id`、`install_domain`、`missing_facts` |
| `precheck` | 判断能否安装 | `installer_backend`、`precheck_outcome`、`blocking_reason` |
| `install` | 在目标环境执行安装 | `install_state`、`install_command`、`workspace_state` |
| `verify` | 验证安装结果 | `verify_state`、`runtime_ready`、`next_action` |

四阶段必须按顺序推进。`precheck_outcome=blocked` 时终止在 `precheck`；`install` 失败时不得继续 `verify`；`verify` 失败时不得交回 runtime。

各阶段输入、决策树、模板选择与失败语义见 `./references/install_rules.md`。

## 3. Discover 门禁（硬约束）

1. 加载本技能后，若上游未提供可靠 `execution_mode`，**第一条 Shell 命令只能是** `./references/install_flow.md` 的 `§0`。
2. `§0` 执行后、下一条 Shell 之前，必须先汇报：

```
execution_mode=<local_slurm|remote_slurm>
IN_CONTAINER=<yes|no>
hostname=<§0 输出>
next_step=<主机发现仅 remote | 硬件探测>
```

3. 在 `execution_mode` 未确认前，**禁止**执行 `install_flow.md` 的 `§3`–`§8`（安装或验证）。
4. `IN_CONTAINER=no` 时视为 `remote_slurm`，**无需再问**「装在本机还是远程」；**严禁**在本端 shell 执行 `conda`、`git clone` 或 `install.sh`。
5. `remote_slurm` 在 SSH 四元组齐备前，本 shell 只允许 `§0`、读取 `onescience.json` / `~/.ssh/config`，以及 `./references/install_rules.md` §5 允许的 SSH 补问。

主机发现、领域映射、硬件探测与 backend 识别细则见 `./references/install_rules.md` §1。

## 4. 阶段执行要点

| 阶段 | 进入条件 | 动作摘要 |
|------|----------|----------|
| `precheck` | `discover` 完成且 `missing_facts` 已补齐 | 读 `install_rules.md` §2，核对 support matrix 与 driver_stack readiness |
| `install` | `precheck_outcome=ready_to_install` | 读 `install_flow.md` 渲染并执行安装命令；细则见 `install_rules.md` §3 |
| `verify` | `install` 命令成功完成 | 读 `install_flow.md` 渲染并执行 verify 命令；细则见 `install_rules.md` §4 |

## 5. 用户交互

只在 SSH 四元组仍缺、多个 Host 需择一、或完全无法映射安装领域时询问用户。细则见 `./references/install_rules.md` §5。

## 6. 最终输出

每次阶段汇报或终止时，至少包含：

- `install_state`
- `precheck_outcome`
- `installed_env_summary`
- `blocking_reason`
- `next_action`

失败处理矩阵见 `./references/install_rules.md` §6。

## 7. 参考文件

| 文件 | 用途 |
|------|------|
| `./references/install_flow.md` | 可渲染命令模板（§0–§8） |
| `./references/install_rules.md` | discover / precheck / install / verify 细则与占位符渲染 |
| `./assets/backend_profiles.json` | installer backend：module、Conda、verify 口径 |
| `./assets/workspace_bootstrap_profiles.json` | 仓库获取、同步与 `install.sh` 入口 |
| `./assets/install_domains.json` | 安装领域到 `{dependency_selector}` 的映射 |
| `./assets/phase_examples/` | 四阶段结构化示例 |
| `./assets/resolution_examples/` | 安装请求 resolution 示例 |
| `skills/onescience-runtime/assets/backend_specs.json` | installer support matrix |
| `skills/onescience-runtime/assets/execution_profiles.json` | runtime/install profile registry |
