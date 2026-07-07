# 为 OpenCode 安装 OneSkills

使用仓库内置的 OpenCode 插件，即可在 OpenCode 中启用 OneScience / OneSkills 技能。该方式会将集成保持在当前克隆仓库内完成，不依赖 Python。

## 单句用户提示词

用户可以将下面这句话直接粘贴到 OpenCode 中：

```text
请获取并按照 https://github.com/onescience-ai/oneskills/blob/master/.opencode/INSTALL.md 中的说明，从当前仓库检出为 OpenCode 安装 OneSkills。
```

如有需要，OpenCode 应自动更新本地 `opencode.json`，将其指向 `.opencode/plugins/oneskills.js`；在配置变更后应提示用户重启；除非默认插件流程失败，否则不应要求用户手动查找技能路径。

## 前置条件

- 已安装 [OpenCode.ai](https://opencode.ai)
- 已在本地检出当前仓库
- 如果用户需要远程获取本文件，则需具备访问 GitHub 的网络能力

## 安装

将本地插件加入 OpenCode 配置中的 `plugin` 数组。

### 项目级配置

如果你只想在当前仓库中启用 OneSkills，请在项目的 `opencode.json` 中加入以下内容：

```json
{
  "plugin": [".opencode/plugins/oneskills.js"]
}
```

### 全局配置

如果你想从全局 OpenCode 配置中加载当前仓库检出，请改为使用插件文件的绝对路径：

```json
{
  "plugin": ["/absolute/path/to/oneskills/.opencode/plugins/oneskills.js"]
}
```

在 Windows 上，示例如下：

```json
{
  "plugin": ["D:\\path\\to\\oneskills\\.opencode\\plugins\\oneskills.js"]
}
```

如果 `plugin` 已存在，请在保留原有插件的前提下追加 OneSkills 条目，而不是直接覆盖整个数组。

保存配置后，重启 OpenCode。

## 该插件会加载什么

位于 `.opencode/plugins/oneskills.js` 的本地插件会：

- 自动注册仓库内的 `skills/` 目录
- 在用户的第一条消息中注入 OneSkills 启动提示
- 将 OneSkills 提示词映射到 OpenCode 原生工具
- 将整个集成保持为当前仓库内的自包含方案

这意味着在使用该插件时，通常无需再手动向 `opencode.json` 添加 `skills.paths`。

## 验证

在重启 OpenCode 前，请先确认插件文件存在：

```text
.opencode/plugins/oneskills.js
```

重启 OpenCode 后，可以尝试以下任一提示词：

```text
使用 oneskills
```

```text
进入 onescience
```

```text
use skill tool to list skills
```

预期行为是：OneSkills 会通过 `onescience-workflow` 路由通用的 OneScience 请求。

## 故障排查

### 插件未加载

1. 检查 `.opencode/plugins/oneskills.js` 是否存在。
2. 确认 `opencode.json` 中的 `plugin` 条目指向了正确路径。
3. 修改配置后重启 OpenCode。
4. 如果你配置的是全局路径，请确认它指向的是当前仓库检出位置。

### 未找到技能

1. 使用 `skill` 工具列出已发现的技能。
2. 确认仓库中仍然存在 `skills/onescience-workflow/SKILL.md`。
3. 确认插件已成功加载。
4. 如果你的环境中插件流程受限，可退回为通过 OpenCode 的技能路径配置显式添加仓库 `skills/` 目录。

### 仓库位置发生变化

如果你移动了当前仓库，请同步更新所有全局 `opencode.json` 中仍指向旧路径的插件配置。

## 更新

拉取仓库最新变更后，重启 OpenCode，以便从更新后的检出中重新加载插件和技能。

## 卸载

从 `opencode.json` 中移除 OneSkills 的插件条目，然后重启 OpenCode。
