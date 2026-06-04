# Install Rules — 流程细则

本文件承载 `discover / precheck / install / verify` 的详细裁决规则。硬门禁与阶段轮廓见 `../SKILL.md`；可渲染命令模板见 `./install_flow.md`。

## 目录

- [§1 Discover 细则](#1-discover-细则)
- [§2 Precheck 规则](#2-precheck-规则)
- [§3 Install 规则](#3-install-规则)
- [§4 Verify 规则](#4-verify-规则)
- [§5 用户交互规则](#5-用户交互规则)
- [§6 失败处理](#6-失败处理)

---

## 1. Discover 细则

### 1.1 优先消费的上游信息

- `skills/onescience-runtime/assets/execution_profiles.json`
- `skills/onescience-runtime/assets/backend_specs.json`
- 运行链路或硬件感知链路产出的 `hardware_profile`
- 用户请求中的安装领域，例如 `earth`、`cfd`、`bio`、`matchem`、`all`

### 1.2 执行域判定

若上游未给出可靠 `execution_profile`，用 `install_flow.md` 的 `§0` 判定当前 shell 是否已在目标容器/登录节点内：

- `IN_CONTAINER=yes`：视为 `local_slurm`，当前 shell 就是安装目标，禁止再 `ssh`
- `IN_CONTAINER=no`：视为 `remote_slurm`，必须先完成主机发现

### 1.3 主机发现（remote_slurm）

顺序：

1. 读取 `onescience.json` 的 `runtime.remote`
2. 读取 `~/.ssh/config`
3. 仍缺 `user`、`host`/`hostname`、`port`、`identity_file` 中任一项时，只询问缺失项
4. 多个 Host 候选时，只询问选哪一个

`{ssh_server}` 优先 `hostname`，否则 `host`。

### 1.4 安装领域解析

- 用户话术命中 `./assets/install_domains.json` 时直接映射为 `install_domain` 和 `{dependency_selector}`
- 完全没有领域信息时再询问用户
- 领域只表达依赖选择，不应混入 host、module、workspace 等环境参数

### 1.5 硬件探测与 backend 识别

如果没有上游 `hardware_profile`，在目标环境执行 `install_flow.md` 的 `§1`（`remote_slurm`）或 `§1b`（`local_slurm`），并按下表生成 `required_backend_id`：

| 优先级 | 探测信号 | `required_backend_id` |
|--------|----------|-----------------------|
| 1 | `module avail` 输出含 `dtk` 或 `sghpc` | `slurm_dcu` |
| 2 | `hipcc` 可用，或存在 `/opt/dtk-*` | `slurm_dcu` |
| 3 | `nvidia-smi` 有 GPU 且 `/usr/local/cuda*` 存在 | `slurm_gpu` |
| 4 | 以上皆不满足 | `slurm_cpu`，随后在 `precheck` 阻断 |

**常见误判（禁止）：**

- 登录节点没有 `nvidia-smi`、`hipcc` 或 `/opt/dtk-*` 不能单独判定为非 DCU
- 超算 DCU 环境常只在 `module avail` 中暴露 DTK/SGHPC 模块

### 1.6 安装通道边界

当前稳定安装通道是 `remote_slurm` 和 `local_slurm`。`remote_direct` / `scnet_mcp` 若在 profile registry 中绑定到 `installer_backend=none`，应在 `precheck` 阶段阻断或交回上游，不要伪造 SSH 安装命令。

---

## 2. Precheck 规则

`precheck` 必须区分两件事：

- backend 是否支持安装：来自 `backend_specs.json` 的 `support_matrix.installer` 或 `support_matrix.local_installer`
- 当前 host 是否满足安装前置条件：来自 `hardware_profile.software.driver_stack`

决策顺序：

1. 根据 `required_backend_id` 和 `execution_mode` 选择 installer backend：
   - `remote_slurm` 使用 `support_matrix.installer`
   - `local_slurm` 优先使用 `support_matrix.local_installer`
2. 若 installer backend 为 `none` 或状态不是 `supported`，输出 `precheck_outcome=blocked`、`blocking_reason=backend_not_supported`
3. 解析 `./assets/backend_profiles.json`，确认安装范围为 `user_space_only`
4. 解析 `./assets/workspace_bootstrap_profiles.json`，确认有 stable workspace bootstrap profile
5. 解析 `./assets/install_domains.json`，确认领域支持所选 installer backend
6. 检查 `driver_stack.driver_ready`、`driver_stack.user_space_ready`、`capability_readiness.compiler_ready`、`torch_ready`、`distributed_runtime_ready`
7. 任一前置条件为 false 时阻断，并按 `driver_stack_not_ready`、`compiler_not_ready`、`torch_not_ready`、`distributed_runtime_not_ready` 给出原因

这些 readiness 表示目标环境中可用于安装与验证的基线能力。驱动、平台 runtime、编译链、分布式通信栈不属于本技能可修复范围；不要在 install 阶段偷偷绕过。

CPU backend 当前 `runtime` 可稳定识别，但 installer 未开放；应阻断为 `backend_not_supported`。

---

## 3. Install 规则

只有 `precheck_outcome=ready_to_install` 才能进入 `install`。

### 3.1 命令渲染约束

- 命令模板只从 `./install_flow.md` 取
- 所有占位符必须先由 profile 或用户输入解析完成
- `remote_slurm` 的探测、安装、验证各自只执行一次 SSH 命令，形式为 `ssh ... 'bash -lc "... && ..."'`
- `local_slurm` 不包 `ssh`
- 安装命令与验证命令分开执行；不要把 verify 拼进 install 命令
- 安装命令必须是同一目标环境上的一条 `&&` 命令串
- 不能混用 DCU 与 GPU 模板

### 3.2 渲染来源

- Conda 环境名与 Python 版本来自 `backend_profiles.json.defaults`
- module 顺序来自 `backend_profiles.json.bootstrap.module_sequence`
- repo、ref、工作区同步和 `bash install.sh` 入口来自 `workspace_bootstrap_profiles.json`
- `{dependency_selector}` 来自 `install_domains.json`

### 3.3 占位符渲染规则

| 占位符 | 规则 |
|--------|------|
| `{ssh_port}`、`{ssh_identity}`、`{ssh_user}`、`{ssh_server}` | 来自 `onescience.json` 的 `runtime.remote` 或 `~/.ssh/config` |
| `{env_name}`、`{python_version}` | 来自已选 `backend_profiles.json` 条目的 `defaults` |
| `{repo_url}`、`{repo_ref}` | 来自已选 `workspace_bootstrap_profiles.json` 的 `repo` |
| `{repo_dir}` | 取 `repo.repo_name`，渲染为 `~/{repo_name}`；当前 stable profile 默认 `~/onescience` |
| `{ssh_options}` | 读取 `onescience.json` 的 `runtime.remote.strict_host_key_checking`；为 `no` 时填 `-o StrictHostKeyChecking=no`；首次连接 SCnet 等未知 host 时建议填入，否则留空 |
| `{dependency_selector}` | 来自 `install_domains.json`；当值为 `all` 且 workspace profile 的 `omit_selector_when_default=true` 时，末尾渲染为 `bash install.sh`（不带参数） |

### 3.4 模板章节选择

| `execution_mode` | 硬件类型 | 探测 | 安装 | 验证 |
|------------------|----------|------|------|------|
| `remote_slurm` | DCU | `§1` | `§3` | `§4` |
| `remote_slurm` | GPU | `§1` | `§5` | `§6` |
| `local_slurm` | DCU | `§1b` | `§7` 安装段 | `§7` 验证段 |
| `local_slurm` | GPU | `§1b` | `§8` 安装段 | `§8` 验证段 |

---

## 4. Verify 规则

`verify` 必须激活安装阶段使用的 Conda 环境，然后执行 backend profile 声明的 verify 命令：

```bash
pip list | grep torch && pip list | grep onescience
```

结果语义：

| 结果 | `verify_state` | `runtime_ready` | `next_action` |
|------|----------------|-----------------|---------------|
| 两类包均可见 | `verified` | `true` | `onescience-runtime` |
| 任一包不可见 | `verify_failed` | `false` | `onescience-installer` |

禁止用 `python -c 'import torch'` 或 `python -c 'import onescience'` 替代本技能的 verify 口径。若仅 `LD_LIBRARY_PATH` 缺失，可在同一 verify 命令前补 `export` 后重试一次；仍失败则停在 `verify_failed`。

---

## 5. 用户交互规则

只在以下情况询问用户：

- `remote_slurm` 主机发现后仍缺 SSH 四元组中的字段
- `~/.ssh/config` 或配置文件给出多个 Host，必须择一
- 用户请求完全没有安装领域，且无法从上下文映射到 `install_domains.json`

其余情况应通过读取资产、执行模板和汇报阶段状态推进，不要把内部 backend/profile 选择反复抛给用户。

---

## 6. 失败处理

| 失败点 | 处理 |
|--------|------|
| SSH 超时或认证失败 | 重试一次；仍失败则 `blocked` |
| 缺 SSH 字段且用户补齐后仍不完整 | `blocked`，列出缺失字段 |
| backend 不支持安装 | `precheck_outcome=blocked`、`blocking_reason=backend_not_supported` |
| 驱动或平台 runtime 未 ready | `precheck_outcome=blocked`，说明需平台侧处理 |
| module/conda/git/install.sh 非零退出 | `install_state=blocked`，报告退出码和末尾日志摘要 |
| verify 无 torch 或 onescience | `verify_state=verify_failed`，不交回 runtime |
