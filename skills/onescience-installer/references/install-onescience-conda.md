# 工作流 - 在 Conda 环境中安装 OneScience

当用户要安装 OneScience，且目标路径是创建或复用 Conda 环境时读取本工作流。

## 前置条件

- 用户已经明确同意创建或复用 Conda 环境。
- `env_name` 已从 `runtime.conda.env_name` 或 `assets/backend_profiles.json` 获取。
- `install_domain` 已通过 `assets/install_domains.json` 映射。
- `repo_url`、`repo_ref`、`repo_dir` 已从 `assets/workspace_bootstrap_profiles.json` 获取。

## 步骤

1. 若没有硬件 profile，先探测硬件：
   - 远程：`install_flow.md` 的 `§1`
   - 本地：`install_flow.md` 的 `§1b`
2. 选择 backend profile：
   - DCU 远程/本地：`dcu_remote_install` 或 `dcu_local_install`
   - GPU 远程/本地：`gpu_remote_install` 或 `gpu_local_install`
   - CPU：阻断，`blocking_reason=backend_not_supported`
3. 在执行任何 `conda env list`、`conda create`、`conda activate` 前，必须先按 `install_flow.md` 的 `{module_init}` + `{conda_recovery}` 逻辑确保 `conda` 可用；若经过 module 恢复和 profile fallback 后仍不可用，返回阻断，不继续安装。
4. 选择安装模板：
   - 远程 DCU 新建 Conda：`§3`
   - 远程 DCU 复用 Conda：`§3a`
   - 远程 GPU 新建 Conda：`§5`
   - 远程 GPU 复用 Conda：`§5a`
   - 本地 DCU 新建 Conda：`§7` 安装段
   - 本地 DCU 复用 Conda：`§7a` 安装段
   - 本地 GPU 新建 Conda：`§8` 安装段
   - 本地 GPU 复用 Conda：`§8a` 安装段
5. 执行安装命令。
6. 执行匹配的验证命令：
   - 远程 DCU：`§4`
   - 远程 GPU：`§6`
   - 本地 DCU：`§7` 或 `§7a` 验证段
   - 本地 GPU：`§8` 或 `§8a` 验证段
7. 验证成功后读取 `writeback-conda-state.md`，只写回 `runtime.conda.enabled=true` 及相关 conda 信息。
8. 写回成功后，若存在上游调用方或 `resume_target` / `resume_phase`，返回调用方继续执行；若没有明确调用方，则设置 `next_action=onescience-orchestrator`。

验证通过前不得写入成功状态。
