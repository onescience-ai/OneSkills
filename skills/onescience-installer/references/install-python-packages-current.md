# 工作流 - 在当前环境中安装 Python 包

当用户要求把 Python 包直接安装到当前目标环境时读取本工作流。

## 前置条件

- 已获得包名列表。
- 用户已经明确同意直接在当前环境安装。
- 包名列表不得包含 `onescience`；若发现 `onescience`（大小写不敏感，含版本约束或 extras），立即停止本工作流并路由到 `install-onescience-current.md`。

## 步骤

1. 预检测目标包是否已存在：
   - 远程当前环境：`install_flow.md` 的 `§15b`
   - 本地当前环境：`install_flow.md` 的 `§17`
2. 若所有包都已存在，询问用户是否仍继续重装或升级。
3. 若存在缺失包，询问用户是否安装到当前环境。
4. 执行安装：
   - 远程当前环境：`§18`
   - 本地当前环境：`§13`
5. 执行验证：
   - 远程当前环境：`§19`
   - 本地当前环境：`§14`
6. 验证成功后读取 `writeback-conda-state.md`，只写回 `runtime.conda.enabled=false`。

本工作流禁止渲染 `conda create` 或 `conda activate`。
