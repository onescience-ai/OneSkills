# 为 Claude Code 安装 OneSkills

使用 Claude Code 插件系统即可在 Claude Code 中启用 OneScience / OneSkills 技能。该方式适合让 Claude 智能体根据自然语言提示自动完成安装，并通过 Claude Code 的 `/plugin` 命令管理插件。

## 单句用户提示词

用户可以将下面这句话直接粘贴到 Claude Code 中：

```text
请获取并按照 https://github.com/onescience-ai/oneskills/blob/master/.claude/install.md 中的说明，为 Claude Code 安装 OneSkills 技能。
```

Claude 应自动执行适合当前环境的插件安装命令，优先使用 Claude Code 的 `/plugin marketplace add` 和 `/plugin install` 安装仓库中的 skills。安装完成后提示用户重启 Claude Code，或在支持的版本中执行 `/reload-plugins`。除非 Claude Code 插件流程失败，否则不应要求用户手动查找、复制或配置技能路径。

## 前置条件

- 已安装 Claude Code
- 具备访问 GitHub 的网络能力
- 当前 Claude Code 版本支持 `/plugin` 插件命令

## 安装

优先添加公开 OneSkills marketplace：

```text
/plugin marketplace add https://github.com/onescience-ai/oneskills
```

然后安装 OneSkills 插件：

```text
/plugin install oneskills@oneskills
```

安装完成后，重启 Claude Code，以便重新发现技能。如果当前 Claude Code 版本支持热重载，也可以执行：

```text
/reload-plugins
```

## 无 /plugin CLI 安装

`/plugin` 命令需要在 Claude Code CLI 的交互环境中执行。如果当前安装流程由其他智能体、脚本环境或无法输入 Claude Code slash command 的终端完成，可以手动安装 skills。手动安装会把仓库中的 `skills/` 复制到 Claude Code 可发现的用户级 `~/.claude/skills` 目录。

手动安装只安装技能内容，不注册 Claude Code 插件 marketplace 元数据。优先使用 `/plugin`；只有无法进入 Claude Code CLI 执行 `/plugin` 时再使用本节方式。

### macOS / Linux

```bash
repo="$HOME/.claude/oneskills"
skills_dir="$HOME/.claude/skills"

if [ -d "$repo/.git" ]; then
  git -C "$repo" pull
else
  git clone https://github.com/onescience-ai/oneskills.git "$repo"
fi

mkdir -p "$skills_dir"
for installed in "$skills_dir"/onescience-* "$skills_dir"/scnet-chat; do
  [ -e "$installed" ] || continue
  name="$(basename "$installed")"
  if [ ! -d "$repo/skills/$name" ]; then
    rm -rf "$installed"
  fi
done

for skill_dir in "$repo"/skills/*; do
  [ -d "$skill_dir" ] || continue
  name="$(basename "$skill_dir")"
  rm -rf "$skills_dir/$name"
  cp -R "$skill_dir" "$skills_dir/"
done
```

### Windows PowerShell

```powershell
$repo = Join-Path $env:USERPROFILE ".claude\oneskills"
$skillsDir = Join-Path $env:USERPROFILE ".claude\skills"

if (Test-Path -LiteralPath (Join-Path $repo ".git")) {
  git -C $repo pull
} else {
  git clone https://github.com/onescience-ai/oneskills.git $repo
}

New-Item -ItemType Directory -Force -Path $skillsDir
$repoSkillsDir = Join-Path $repo "skills"
Get-ChildItem -LiteralPath $skillsDir -Directory -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -like "onescience-*" -or $_.Name -eq "scnet-chat" } |
  ForEach-Object {
    if (-not (Test-Path -LiteralPath (Join-Path $repoSkillsDir $_.Name))) {
      Remove-Item -LiteralPath $_.FullName -Recurse -Force
    }
  }

Get-ChildItem -LiteralPath $repoSkillsDir -Directory | ForEach-Object {
  $target = Join-Path $skillsDir $_.Name
  Remove-Item -LiteralPath $target -Recurse -Force -ErrorAction SilentlyContinue
  Copy-Item -LiteralPath $_.FullName -Destination $target -Recurse -Force
}
```

手动安装完成后，重启 Claude Code，或执行 `/reload-plugins`。如果你的 Claude Code 版本配置了不同的用户级 skills 目录，请把上面命令中的 `~/.claude/skills` 替换为实际目录。

## 本地检出安装

如果你已经在本地检出了 OneSkills 仓库，并希望从当前仓库安装，请从仓库父目录启动 Claude Code，然后添加本地 marketplace。

例如仓库位于 `~/oneskills` 时：

```text
/plugin marketplace add ./oneskills
```

然后安装插件：

```text
/plugin install oneskills@oneskills
```

不要把 `./oneskills/.claude-plugin` 作为本地 marketplace 路径。该目录中保存 marketplace 元数据，但插件 source 指向仓库根目录，Claude Code 需要从仓库根目录安装完整插件，才能包含顶层的 `skills/` 目录。

安装完成后，重启 Claude Code，或执行 `/reload-plugins`。

## 安装内容

Claude Code 会读取仓库内的 `.claude-plugin/marketplace.json` 和 `.claude-plugin/plugin.json`，并安装仓库顶层 `skills/` 目录中的技能。通常无需手动配置技能路径，也无需手动复制 `skills/` 目录。

当前仓库包含的技能包括：

- `onescience-cli`
- `onescience-coder`
- `onescience-data-analyzer`
- `onescience-data-profile`
- `onescience-dataset-builder`
- `onescience-infer`
- `onescience-installer`
- `onescience-orchestrator`
- `onescience-paper-repro`
- `onescience-parallel`
- `onescience-primitives`
- `onescience-research-workflow`
- `onescience-runtime`
- `scnet-chat`

## 验证

重启 Claude Code 后，可以先打开插件管理器：

```text
/plugin
```

确认 `oneskills` 出现在已安装插件列表中。然后尝试以下提示词：

```text
使用 oneskills
```

```text
进入 onescience
```

```text
使用 onescience-coder 技能，帮我分析当前项目需要改哪些代码
```

预期行为是：Claude Code 能发现 OneSkills 技能，并在用户提出科研工作流、代码实现、运行、安装、数据处理或论文复现等请求时，选择匹配的技能。

## 更新

重新从 marketplace 安装即可更新到最新 OneSkills：

```text
/plugin marketplace add https://github.com/onescience-ai/oneskills
```

```text
/plugin install oneskills@oneskills
```

更新后重启 Claude Code，或执行 `/reload-plugins`。

## 卸载

移除 OneSkills 插件：

```text
/plugin uninstall oneskills
```

如果你的 Claude Code 插件管理器显示了不同的本地安装名，请以 `/plugin` 中列出的实际名称为准。

## 故障排查

### /plugin 命令不可用

1. 确认当前使用的是 Claude Code，而不是普通 Claude 对话界面。
2. 更新 Claude Code 到支持插件系统的版本。
3. 重新启动 Claude Code 后再尝试安装。
4. 如果仍然无法使用 `/plugin`，改用本文的“无 /plugin CLI 安装”手动复制方式。

### 无法访问 GitHub

1. 确认当前环境可以访问 `https://github.com/onescience-ai/oneskills`。
2. 如果远程 marketplace 无法访问，可以先在可联网环境克隆仓库，再使用“本地检出安装”方式。
3. 本地安装时确认 `/plugin marketplace add` 指向仓库根目录，而不是 `.claude-plugin/` 子目录。

### 未发现技能

1. 确认 `/plugin install oneskills@oneskills` 已成功完成。
2. 重启 Claude Code，或执行 `/reload-plugins`。
3. 在 `/plugin` 中确认 `oneskills` 已安装。
4. 确认安装源中存在 `skills/onescience-research-workflow/SKILL.md`。
5. 如果使用本地检出安装，确认 marketplace 路径是仓库根目录。
6. 如果使用手动安装，确认 `~/.claude/skills/onescience-research-workflow/SKILL.md` 存在。

### 本地仓库位置发生变化

如果你使用本地检出安装并移动了仓库，请重新从新的仓库父目录执行：

```text
/plugin marketplace add ./oneskills
```

然后重新安装插件并重启 Claude Code：

```text
/plugin install oneskills@oneskills
```
