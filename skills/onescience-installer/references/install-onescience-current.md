# 工作流 - 在当前环境中安装 OneScience

当用户要直接在当前目标环境安装 OneScience，且不创建、不激活 Conda 时读取本工作流。

## 前置条件

- 用户已经明确同意直接在当前环境安装。
- `install_domain` 已通过 `assets/install_domains.json` 映射。
- 仓库 profile 已从 `assets/workspace_bootstrap_profiles.json` 获取。

## 步骤

1. 若没有硬件 profile，先探测硬件：
   - 远程：`install_flow.md` 的 `§1`
   - 本地：`install_flow.md` 的 `§1b`
2. 选择 backend；CPU 仍然阻断。
3. 选择安装模板：
   - 远程 DCU 当前环境：`§3b`
   - 远程 GPU 当前环境：`§5b`
   - 本地 DCU 当前环境：`§7b` 安装段
   - 本地 GPU 当前环境：`§8b` 安装段
4. 执行安装命令。
5. 执行验证命令：
   - 远程 DCU 当前环境：`§4b`
   - 远程 GPU 当前环境：`§6b`
   - 本地 DCU 当前环境：`§7b` 验证段
   - 本地 GPU 当前环境：`§8b` 验证段
6. 验证成功后读取 `writeback-conda-state.md`，只写回 `runtime.conda.enabled=false`。

本工作流禁止渲染 `conda create` 或 `conda activate`。
