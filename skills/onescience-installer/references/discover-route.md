# 工作流 - 发现与路由

每次安装任务都先读取本工作流。读取本文件前，`SKILL.md` 中的运行站点门禁必须已经通过；若 `run_site` 或远程 SSH 信息缺失，先执行 `runsite-handoff.md`。

## 步骤

1. 重新读取根目录 `onescience.json`，不要使用 runsite 执行前的旧缓存。
2. 解析 `runtime.execution_profile.run_site`：
   - `local`：后续渲染 `install_flow.md` 中的本地模板。
   - `remote`：后续渲染 `install_flow.md` 中的 SSH 模板。
3. 当 `run_site=remote` 时，必须从 `runtime.ssh` 获取 `host/hostname`、`port`、`user`、`identity_file`；缺失时返回 `blocking_reason=runsite_required`，重新路由到 `runsite-handoff.md`。
4. **检查上游委托原因**：若上游调用方传入 `installer_reason=workspace_model_path_detected`，跳过步骤 5-10 的意图识别和环境检测，直接跳转到步骤 11（workspace 模型路径自动发现）。此时 conda 环境已就绪，仅需探测并写回模型路径。
5. 先识别用户意图：
   - 安装 OneScience 环境：`install_intent=bootstrap`。
   - 安装 Python 或 pip 包：`install_intent=python_packages`。
   - 意图不明确：只询问用户选择"安装 OneScience 环境"还是"安装 Python 包"，不要继续路由。
6. 对 `onescience` 做强制归类：
   - 用户说“安装 onescience 包”“pip install onescience”“安装 OneScience 环境”都必须归为 `install_intent=bootstrap`。
   - 解析普通 Python 包列表时，`onescience`（大小写不敏感，含版本约束如 `onescience==...`、extras 如 `onescience[...]`）不得进入 `{python_packages}`。
   - 若请求同时包含 `onescience` 和其它包，先把 `onescience` 路由到 bootstrap 分支；其它普通包只能在 OneScience 安装验证成功后，按用户同意继续走 Python 包分支。
7. 若 `install_intent=bootstrap`，从用户请求或上下文解析安装领域，并通过 `assets/install_domains.json` 映射；无法映射时询问领域或 `all`。
8. 若 `install_intent=python_packages`，解析包名列表；缺少包名时只询问包名；包名列表中若只剩 `onescience`，立即改路由到 bootstrap，不读取 Python 包安装工作流。
9. 解析 `runtime.conda`：
   - 缺失：先路由到 `detect-existing-onescience.md`。
   - `enabled=true`：记录 `env_name` 和 `activate_script`，后续可进入 Conda 路径。
   - `enabled=false`：默认进入当前环境路径，除非用户明确选择创建 Conda。
10. 保留上游传入的 `resume_target`、`resume_phase` 或等价 handoff 上下文，供安装成功后回传给调用方继续执行。
11. 读取 `assets/backend_profiles.json`，获得默认 `env_name`、`python_version`、module 顺序与 verify 命令。
12. **Workspace 模型路径自动发现**：在检测或安装环境后，自动探测 workspace 中是否存在模型权重目录和对应的 `env.sh`。详细步骤见 `./references/workspace-model-path-discovery.md`。发现后，将模型路径写入 `onescience.json.runtime.script.env_vars.ONESCIENCE_MODELS_DIR` 和 `ONESCIENCE_DATASETS_DIR`（如果用户未显式覆盖）。

## 路由判定

- `installer_reason=workspace_model_path_detected`：跳过 conda/Python 包路由，直接读取 `workspace-model-path-discovery.md`，完成后返回上游调用方。
- `runtime.conda` 缺失：读取 `detect-existing-onescience.md`。
- `install_intent=bootstrap` 且用户选择 Conda 路径：读取 `install-onescience-conda.md`。
- `install_intent=bootstrap` 且用户选择当前环境路径：读取 `install-onescience-current.md`。
- `install_intent=python_packages` 且目标是 Conda 环境：读取 `install-python-packages-conda.md`。
- `install_intent=python_packages` 且目标是当前环境：读取 `install-python-packages-current.md`。

发现阶段不得执行安装命令。
发现阶段若识别到 `onescience` 被当作普通包传入，必须先修正路由；不得把该错误留到 `pip install` 模板渲染时才处理。
