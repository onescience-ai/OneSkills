# 工作流 - 运行站点配置交接

当无法从根目录 `onescience.json` 获取完整运行站点配置时，读取本工作流。

## 触发条件

满足任一条件时必须触发：

- `onescience.json` 不存在。
- `onescience.json.runtime.execution_profile.run_site` 缺失或不是 `local|remote`。
- `run_site=remote`，但 `onescience.json.runtime.ssh` 缺少 `host/hostname`、`port`、`user`、`identity_file` 中任一项。

## 处理步骤

1. 停止 onescience-installer 当前安装流程，不要执行包检测、安装或 verify。
2. 读取并调用 `skills/onescience-runsite/SKILL.md`。
3. 按 `onescience-runsite` 的规则补齐或生成运行站点配置；runsite 只负责配置发现、补问、保存和交接，不执行安装。
4. runsite 成功后，必须重新读取根目录 `onescience.json`。
5. 若重新读取后仍缺少 `run_site` 或远程 SSH 信息，返回：
   - `install_state=blocked`
   - `blocking_reason=runsite_config_incomplete`
   - `next_action=onescience-runsite`
6. 若配置完整，回到 `discover-route.md` 重新识别意图与路由。

## 成功条件

`onescience.json` 至少包含：

- `runtime.execution_profile.run_site`
- 当 `run_site=remote` 时，包含完整 `runtime.ssh`

不要把 runsite 的交接物当成环境探测结果；onescience-installer 后续仍需按自身工作流执行检测、安装和验证。
