# 工作流 - 发现与路由

每次安装任务都先读取本工作流。读取本文件前，`SKILL.md` 中的运行站点门禁必须已经通过；若 `run_site` 或远程 SSH 信息缺失，先执行 `runsite-handoff.md`。

## 步骤

1. 重新读取根目录 `onescience.json`，不要使用 runsite 执行前的旧缓存。
2. 解析 `runtime.execution_profile.run_site`：
   - `local`：后续渲染 `install_flow.md` 中的本地模板。
   - `remote`：后续渲染 `install_flow.md` 中的 SSH 模板。
3. 当 `run_site=remote` 时，必须从 `runtime.ssh` 获取 `host/hostname`、`port`、`user`、`identity_file`；缺失时返回 `blocking_reason=runsite_required`，重新路由到 `runsite-handoff.md`。
4. 先识别用户意图：
   - 安装 OneScience 环境：`install_intent=bootstrap`。
   - 安装 Python 或 pip 包：`install_intent=python_packages`。
   - 安装 HPC 科学计算软件（如 GROMACS、LAMMPS、VASP、Quantum ESPRESSO 等）：`install_intent=hpc_software`。
   - 意图不明确：只询问用户选择“安装 OneScience 环境”“安装 Python 包”还是“安装 HPC 软件”，不要继续路由。
5. 对 `onescience` 做强制归类：
   - 用户说“安装 onescience 包”“pip install onescience”“安装 OneScience 环境”都必须归为 `install_intent=bootstrap`。
   - 解析普通 Python 包列表时，`onescience`（大小写不敏感，含版本约束如 `onescience==...`、extras 如 `onescience[...]`）不得进入 `{python_packages}`。
   - 若请求同时包含 `onescience` 和其它包，先把 `onescience` 路由到 bootstrap 分支；其它普通包只能在 OneScience 安装验证成功后，按用户同意继续走 Python 包分支。
6. 若 `install_intent=bootstrap`，从用户请求或上下文解析安装领域，并通过 `assets/install_domains.json` 映射；无法映射时询问领域或 `all`。
7. 若 `install_intent=python_packages`，解析包名列表；缺少包名时只询问包名；包名列表中若只剩 `onescience`，立即改路由到 bootstrap，不读取 Python 包安装工作流。
8. 若 `install_intent=hpc_software`，从用户请求中解析目标软件名（如 gromacs、lammps），并读取 `assets/hpc_software_profiles.json` 进行匹配：
   - 匹配到唯一 profile：记录软件 id、display_name、version，继续第 9 步。
   - 匹配到多个 profile：列出候选，让用户选择。
   - 无匹配：告知用户当前不支持的软件列表（遍历 `hpc_software_profiles.json[].display_name`），并询问是否安装其他软件。
9. 解析 `runtime.conda`：
   - 缺失：先路由到 `detect-existing-onescience.md`。
   - `enabled=true`：记录 `env_name` 和 `activate_script`，后续可进入 Conda 路径。
   - `enabled=false`：默认进入当前环境路径，除非用户明确选择创建 Conda。
10. 保留上游传入的 `resume_target`、`resume_phase` 或等价 handoff 上下文，供安装成功后回传给调用方继续执行。
11. 读取 `assets/backend_profiles.json`，获得默认 `env_name`、`python_version`、module 顺序与 verify 命令。

## 路由判定

- `runtime.conda` 缺失：读取 `detect-existing-onescience.md`。
- `install_intent=bootstrap` 且用户选择 Conda 路径：读取 `install-onescience-conda.md`。
- `install_intent=bootstrap` 且用户选择当前环境路径：读取 `install-onescience-current.md`。
- `install_intent=python_packages` 且目标是 Conda 环境：读取 `install-python-packages-conda.md`。
- `install_intent=python_packages` 且目标是当前环境：读取 `install-python-packages-current.md`。
- `install_intent=hpc_software`：读取 `install-hpc-software.md`（不需要 conda 环境判断）。

发现阶段不得执行安装命令。
发现阶段若识别到 `onescience` 被当作普通包传入，必须先修正路由；不得把该错误留到 `pip install` 模板渲染时才处理。
发现阶段若 `install_intent=hpc_software`，不需要解析 `runtime.conda`（HPC 软件安装不依赖 conda 环境）；但必须确保 `run_site` 和 remote SSH 信息已就绪。
