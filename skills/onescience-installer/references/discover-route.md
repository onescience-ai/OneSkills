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
   - 意图不明确：只询问用户选择“安装 OneScience 环境”还是“安装 Python 包”，不要继续路由。
5. 若 `install_intent=bootstrap`，从用户请求或上下文解析安装领域，并通过 `assets/install_domains.json` 映射；无法映射时询问领域或 `all`。
6. 若 `install_intent=python_packages`，解析包名列表；缺少包名时只询问包名。
7. 解析 `runtime.conda`：
   - 缺失：先路由到 `detect-existing-onescience.md`。
   - `enabled=true`：记录 `env_name` 和 `activate_script`，后续可进入 Conda 路径；这只表示应复用记录环境，不代表目标端 `conda` 可执行文件已经在 PATH 中，命中 Conda 分支后仍允许按 `install_flow.md` 执行恢复逻辑。
   - `enabled=false`：默认进入当前环境路径，除非用户明确选择创建 Conda。
8. 保留上游传入的 `resume_target`、`resume_phase` 或等价 handoff 上下文，供安装成功后回传给调用方继续执行。
9. 读取 `assets/backend_profiles.json`，获得默认 `env_name`、`python_version`、module 顺序与 verify 命令。

## 路由判定

- `runtime.conda` 缺失：读取 `detect-existing-onescience.md`。
- `install_intent=bootstrap` 且用户选择 Conda 路径：读取 `install-onescience-conda.md`。
- `install_intent=bootstrap` 且用户选择当前环境路径：读取 `install-onescience-current.md`。
- `install_intent=python_packages` 且目标是 Conda 环境：读取 `install-python-packages-conda.md`。
- `install_intent=python_packages` 且目标是当前环境：读取 `install-python-packages-current.md`。

发现阶段不得执行安装命令。
