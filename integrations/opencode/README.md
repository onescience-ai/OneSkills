# OpenCode Integration Notes

本文件提供 `OneSkills` 在 `OpenCode` 类技能代理环境中的最小接入说明。

它不替代 `integrations/generic-agent.md`，而是补充 `OpenCode` 场景下的推荐加载方式。

## 推荐安装布局

使用安装器：

```bash
python3 install/install_oneskills.py --agent opencode --project /your/project
```

全局安装（OpenCode 默认会从 `~/.opencode/skills/` 发现 skill）：

```bash
python3 install/install_oneskills.py --agent opencode --project ~
```

安装后目录：

```text
.opencode/
├── skills/                 # 6 个顶层 skill + 各自内层 references/
├── references/             # 外层共享 references/
├── integrations/
├── onescience/             # OneScience 源码快照（供 coder 读取）
└── opencode.jsonc.snippet  # 可选合并进 opencode.jsonc
```

OpenCode 默认会自动扫描 `.opencode/skills/*/SKILL.md`。因此当 skill 安装在上述默认布局时，**通常不必**修改 `opencode.jsonc`。

若你使用了非默认 `--namespace-root`，或希望在项目级 `opencode.jsonc` 中显式声明路径，可将 snippet 中的 `skills.paths` 合并进去：

```jsonc
{
  "skills": {
    "paths": [".opencode/skills"]
  }
}
```

可选：安装到持久化 vendor 目录：

```bash
python3 install/install_oneskills.py --agent opencode --project /your/project \
  --namespace-root vendor/oneskills/2026.05.15
```

此时 `skills.paths` 应改为 `vendor/oneskills/2026.05.15/skills`，且通常**需要**写入 `opencode.jsonc`。

## 推荐加载方式

建议同时提供：

- `skills/`
- `references/`（含 `catalog_integration.md`）
- `integrations/generic-agent.md`
- `integrations/opencode/README.md`

其中：

- `skills/` 负责核心能力
- `references/catalog_integration.md` 负责 Catalog 与原语/skill 协作
- `integrations/generic-agent.md` 负责通用分层约束
- 本文件负责 `OpenCode` 场景下的补充说明

## Catalog 协作

OpenCode 内置 Catalog 时，Agent 应使用 `catalog_search` / `catalog_resolve`：

- 选 AI 原语：`search(kind=primitive)` → `resolve(location|contract)`
- 选 skill：优先 `<available_skills>`；不足时再 `search(kind=skill)` → `skill` tool
- UI 已写入 `selectedPrimitiveIds` 时跳过 primitive search

官方 skill 清单见仓库 `catalog/manifest.json`；远程索引见 `.well-known/skills/index.json`。

## 推荐行为

1. 如果用户只是说“使用/启动/打开/进入 onescience”或“使用/启动/打开/进入 oneskills”，以及“onescience 模式”“oneskills 模式”，默认进入 `onescience-workflow`，识别为 `general-onescience-request`，先询问具体科研目标，不要直接进入执行层。

2. 如果用户明确点名具体 skill，例如 `onescience-coder`、`onescience-runtime`、`onescience-installer`，则直接使用对应 skill；该 skill 再按自身规则判断是否需要回到 `onescience-workflow`。

3. 默认先走：

```text
onescience-workflow -> onescience-role -> onescience-skill
```

4. 只有任务明确涉及远程 host、GPU/DCU、队列、module、conda 或 slurm 约束时，才进入 `onescience-runtime` 或 `onescience-installer`。

5. 用户未明确要求运行或安装时，不要自动进入：

- `onescience-runtime`
- `onescience-installer`

6. 远程环境缺失时，优先给出缺失项并继续本地代码链，不要直接判定整条任务 blocked。

7. 输出中优先使用仓库相对路径，不要硬编码特定 IDE 或 agent 私有目录。
