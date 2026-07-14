# 为 Codex 安装 OneSkills

使用 Codex marketplace 即可在 Codex 中启用 OneScience / OneSkills 技能。该方式不依赖 Python，适合让 Codex 智能体根据自然语言提示自动完成安装。

## 单句用户提示词

用户可以将下面这句话直接粘贴到 Codex 中：

```text
请获取并按照 https://github.com/onescience-ai/oneskills/blob/master/.codex/INSTALL.md 中的说明，为 Codex 安装 OneSkills 技能。
```

Codex 应自动执行适合当前环境的安装命令，优先使用 `codex-marketplace` 安装仓库中的 skills。安装完成后提示用户重启 Codex。除非 `codex-marketplace` 流程失败，否则不应要求用户手动查找、复制或配置技能路径。

## 前置条件

- 已安装 Codex
- 具备访问 GitHub 的网络能力
- 推荐本机可执行 `npx`；如果没有 `npx`，可使用下面的无 npx 安装方式

## 安装

优先使用 Codex marketplace 从 OneSkills 仓库安装 skills：

```bash
npx codex-marketplace add https://github.com/onescience-ai/oneskills --skills
```

如果当前 Codex 环境要求全局安装，可以改用：

```bash
npx codex-marketplace add https://github.com/onescience-ai/oneskills --skills --global
```

安装完成后，重启 Codex，以便重新发现技能。

## 无 npx 安装

如果当前环境没有 `npx`，但有 `npm`，可以改用 `npm exec`：

```bash
npm exec -- codex-marketplace add https://github.com/onescience-ai/oneskills --skills
```

如果当前环境既没有 `npx`，也不方便使用 `npm exec`，可以手动安装。手动安装会把仓库中的 `skills/` 复制到 Codex 可发现的 `~/.agents/skills` 目录，并清理旧版废弃入口。

### macOS / Linux

```bash
repo="$HOME/.codex/oneskills"
skills_dir="$HOME/.agents/skills"

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
$repo = Join-Path $env:USERPROFILE ".codex\oneskills"
$skillsDir = Join-Path $env:USERPROFILE ".agents\skills"

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

手动安装完成后，重启 Codex。

## 本地检出安装

如果你已经在本地检出了 OneSkills 仓库，并希望从当前仓库安装，请在仓库根目录执行：

```bash
npx codex-marketplace add . --skills
```

如果当前 Codex 环境要求全局安装，可以改用：

```bash
npx codex-marketplace add . --skills --global
```

安装完成后，重启 Codex。

## 安装内容

Codex marketplace 会读取仓库内的 `.codex-plugin/plugin.json`，并安装其中声明的 `./skills/` 目录。通常无需手动配置技能路径，也无需手动复制 `skills/` 目录。

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

重启 Codex 后，可以尝试以下提示词：

```text
使用 oneskills
```

```text
进入 onescience
```

```text
使用 onescience-research-workflow
```

预期行为是：Codex 能发现 OneSkills 技能，并在用户提出科研工作流、代码实现、运行、安装、数据处理或论文复现等请求时，选择匹配的技能。

## 更新

重新从 GitHub 安装即可更新到最新 OneSkills：

```bash
npx codex-marketplace add https://github.com/onescience-ai/oneskills --skills
```

如果使用全局安装：

```bash
npx codex-marketplace add https://github.com/onescience-ai/oneskills --skills --global
```

更新后重启 Codex。

## 卸载

移除通过 marketplace 安装的 OneSkills 技能：

```bash
npx codex-marketplace remove --global --skill --yes onescience-cli
```

如果你的 Codex marketplace 使用了其他本地安装名，请以 `codex-marketplace` 列出的实际名称为准。

## 故障排查

### npx 或 codex-marketplace 不可用

1. 如果有 `npm`，使用 `npm exec -- codex-marketplace add https://github.com/onescience-ai/oneskills --skills`。
2. 如果没有 `npm exec`，使用本文的“无 npx 安装”手动复制方式。
3. 安装后重启 Codex。


### 未发现技能

1. 确认安装命令已成功完成。
2. 重启 Codex。
3. 确认仓库中的 `.codex-plugin/plugin.json` 存在，并且 `skills` 字段指向 `./skills/`。
4. 如果使用本地检出安装，确认安装命令是在仓库根目录执行的。

### 本地仓库位置发生变化

如果你使用本地检出安装并移动了仓库，请重新在新的仓库根目录执行：

```bash
npx codex-marketplace add . --skills
```

然后重启 Codex。
