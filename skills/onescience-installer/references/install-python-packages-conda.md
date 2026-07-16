# 工作流 - 在 Conda 环境中安装 Python 包

当用户要求把 Python 包安装到 Conda 环境时读取本工作流。

## 前置条件

- 已获得包名列表。
- 用户已经明确同意安装到目标 Conda 环境。
- `env_name` 来自 `runtime.conda.env_name`；若用户同意新建环境，则来自 `assets/backend_profiles.json`。

## 步骤

1. 在执行任何 `conda env list`、`conda create`、`conda activate` 前，必须先按 `install_flow.md` 的 `{module_init}` + `{conda_recovery}` 逻辑确保 `conda` 可用；若经过 module 恢复和 profile fallback 后仍不可用，返回阻断，不继续安装。
2. 若 Conda 环境不存在且用户同意创建，只创建并激活环境；不要拉取 OneScience 仓库，也不要执行 `install.sh`。
3. 预检测目标包是否已存在：
   - 远程 Conda：`install_flow.md` 的 `§15`
   - 本地 Conda：`install_flow.md` 的 `§16`
4. 若所有包都已存在，询问用户是否仍继续重装或升级。
5. 若存在缺失包，询问用户是否安装到 `{env_name}`。
6. 执行安装：
   - 远程 Conda：`§9`
   - 本地 Conda：`§11`
7. 执行验证：
   - 远程 Conda：`§10`
   - 本地 Conda：`§12`
8. 验证成功后读取 `writeback-conda-state.md`，只写回 `runtime.conda.enabled=true` 及相关 conda 信息。
9. 写回成功后，若存在上游调用方或 `resume_target` / `resume_phase`，返回调用方继续执行；若没有明确调用方，则设置 `next_action=onescience-orchestrator`。

本工作流禁止拉取 OneScience 仓库，禁止执行 `install.sh`。
