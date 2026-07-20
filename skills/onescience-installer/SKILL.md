---
name: onescience-installer
description: OneScience 环境安装技能。用于根据 onescience.json 安装或验证 OneScience、创建或复用 conda 环境、检测已有 onescience 包、在记录的 conda 环境或当前环境中安装 Python 包；缺少 run_site 或远程 SSH 配置时先调用 onescience-runsite 补齐运行站点配置。
type: executor
---

# OneScience 安装器

## 主流程

1. 读取根目录 `onescience.json`。
2. 校验运行站点配置：
   - 必须能从 `onescience.json.runtime.execution_profile.run_site` 获取 `local` 或 `remote`。
   - 当 `run_site=remote` 时，必须能从 `onescience.json.runtime.ssh` 获取 SSH 信息。
   - 如果缺少 `run_site`，或 `run_site=remote` 但 SSH 信息不完整，读取 `./references/runsite-handoff.md`，调用 `skills/onescience-runsite` 补齐配置；只有 runsite 成功写回或更新 `onescience.json` 后，才能继续安装流程。
3. 读取 `./references/discover-route.md`，识别用户意图、安装领域、Python 包列表、`runtime.conda` 状态和目标环境路径。
4. 根据“意图 + 环境路径 + conda 状态”读取对应分支文件，并且只读取命中的分支文件。
5. 需要渲染探测、安装、验证命令时，读取 `./references/install_flow.md`。
6. OneScience 自身是特殊 bootstrap 目标，不属于普通 Python 包：安装 `onescience`、`OneScience 环境`、`earth/cfd/bio/matchem/all` 时必须下载/同步 `workspace_bootstrap_profiles.json` 指定的仓库到 `{repo_dir}`，进入仓库后执行 `bash install.sh {dependency_selector}`；不得渲染 `pip install onescience`、`python -m pip install onescience` 或把 `onescience` 放入 `{python_packages}`。
7. 检测成功、安装成功且验证成功后，读取 `./references/writeback-conda-state.md` 写回 `onescience.json.runtime.conda`。
8. 写回成功后，若当前任务带有上游 handoff / resume 信息，则返回调用它的技能继续执行；若没有明确调用方，则交回 `onescience-orchestrator` 规划后续任务。

## 必要资产

- `./assets/backend_profiles.json`：环境名、Python 版本、module 顺序、verify 口径。
- `./assets/workspace_bootstrap_profiles.json`：OneScience 仓库和 `install.sh` 入口。
- `./assets/install_domains.json`：`earth/cfd/bio/matchem/all` 到 install selector 的映射。
- `./assets/conda_env.example.json`：成功写回格式示例。

installer 的环境信息写回位置是 `onescience.json.runtime.conda`。除 `runtime.conda` 外，不修改 `onescience.json` 的其它信息。

## 意图识别流程

1. 用户要求“安装 OneScience 环境”“安装 earth/cfd/bio/matchem/all 环境”“安装 onescience 包”“初始化 OneScience 环境”时，设为 `install_intent=bootstrap`。`onescience` 包名大小写不敏感，命中后永远按 bootstrap 处理。
2. 用户要求“安装 Python 包”“安装 pip 包”“补装依赖”“安装某个包到 OneScience 环境”时，设为 `install_intent=python_packages`；但包名列表里若包含 `onescience`，必须拆分并将 `onescience` 路由到 `install_intent=bootstrap`，其余普通 Python 包才允许继续走 pip 分支。
3. 用户没有明确意图时，先询问要安装 OneScience 环境还是安装 Python 包；不要在意图未知时进入安装分支。
4. `install_intent=bootstrap` 必须解析安装领域；无法从请求映射到 `install_domains.json` 时，询问用户安装哪个领域或是否安装 `all`。
5. `install_intent=python_packages` 必须解析包名列表；缺少包名时只询问包名。

## 分支映射

| 前置状态 / 用户意图                                 | 必读工作流 |
|---------------------------------------------|---|
| 缺少 `run_site`，或远程模式缺少 SSH 信息                | `./references/runsite-handoff.md` |
| 进入安装后的通用发现、意图识别、路径判定                        | `./references/discover-route.md` |
| `runtime.conda` 缺失，需要先判断目标环境是否已有 OneScience 包 | `./references/detect-existing-onescience.md` |
| 意图是安装 OneScience，且目标路径是创建或复用 Conda 环境       | `./references/install-onescience-conda.md` |
| 意图是安装 OneScience，且目标路径是当前环境                 | `./references/install-onescience-current.md` |
| 意图是安装 Python 包，且目标路径是 Conda 环境              | `./references/install-python-packages-conda.md` |
| 意图是安装 Python 包，且目标路径是当前环境                   | `./references/install-python-packages-current.md` |
| 检测成功、安装成功并验证成功后需要写回 `onescience.json.runtime.conda` | `./references/writeback-conda-state.md` |

## 硬门禁

- 环境检测阶段（`detect-existing-onescience.md`）：可直接执行检测命令，不需要用户确认；检测完成后只报告结果，不得自动创建环境或安装包。
- 创建 Conda 环境、安装 OneScience、安装 Python 包前：必须获得用户明确同意。
- `run_site=remote` 时，在 SSH 信息齐备前不要执行安装、验证或包检测。
- `run_site=remote` 时不要在本端 shell 执行 `conda`、`git clone`、`install.sh` 或 `pip install`。
- 禁止用 pip 安装 OneScience 自身：任何 `pip install onescience`、`python -m pip install onescience`、`pip install {python_packages}` 且 `{python_packages}` 含 `onescience` 的命令都必须视为错误路由并停止，改走 `install-onescience-conda.md` 或 `install-onescience-current.md`。
- `runtime.conda` 缺失时，必须先走 `detect-existing-onescience.md`；若目标环境已有 `onescience` 和 `torch` 包，写回环境信息到 `runtime.conda` 并返回，不创建环境；若都没有，只报告检测结果，询问是否创建 conda 环境并安装 onescience。
- 已有 `runtime.conda.enabled=true` 时，后续 Conda 路径必须使用记录的 `env_name` 和 `activate_script`。
- 已有 `runtime.conda.enabled=false` 时，默认按当前环境路径处理；除非用户明确同意，否则不要创建 Conda 环境。
- 安装失败或验证失败时，不要写入成功状态。

## 输出契约

阶段汇报和最终输出至少包含：

- `run_site`
- `workflow`
- `install_intent`
- `install_state`
- `verify_state`
- `conda_writeback`
- `next_action`
- `resume_target`
- `resume_phase`
