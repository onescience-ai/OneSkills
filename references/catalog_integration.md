# Catalog Integration

本文件描述 OneSkills 与 OneCode Catalog 的协作约定，供 `onescience-workflow`、`onescience-role`、`onescience-skill` 及 OpenCode 集成说明引用。

## 两类资产

| kind | 发现方式 | 确定后 |
|------|----------|--------|
| `skill` | `<available_skills>` 或 `catalog_search(kind=skill)` | `skill` tool 加载 `SKILL.md` |
| `primitive` | `catalog_search(kind=primitive)` | `catalog_resolve(part=location\|contract)` |

## 何时搜索

### AI 原语（`kind=primitive`）

在以下情况优先搜索：

- 用户要接入数据集、模型、应用或能力资产
- 任务需要确定 `location` / `contract` 后才能写代码或提交运行
- 前端或任务上下文尚未绑定 `selectedPrimitiveIds`

若任务上下文已包含 `selectedPrimitiveIds`（由 UI 写入），则跳过 primitive search，直接 `catalog_resolve`。

### Skills（`kind=skill`）

保持现有 `<available_skills>` 优先：

- 名单已能覆盖用户意图时，直接用 `skill` tool
- 仅在名单不足、语义模糊或新 skill 尚未进入当前会话提示时，再 `catalog_search(kind=skill)`

## 推荐编排

```text
用户任务
  -> （如需资产）catalog_search(primitive)
  -> catalog_resolve(location, contract)
  -> 绑定 selectedPrimitiveIds / 任务上下文
  -> onescience-workflow / onescience-role / onescience-skill
  -> skill tool 或 catalog_search(skill)
  -> onescience-coder / onescience-runtime / onescience-installer
```

多数数据/模型类任务可先原语、后 skill；是否调换由 Agent 按任务决定，Catalog 不强制顺序。

## OneSkills 发布契约

- 官方 skill 清单：`catalog/manifest.json`
- 远程索引：`.well-known/skills/index.json`
- Catalog ingest 只索引 `skills/` 下顶层 skill；`onescience/` 源码树是 coder 依赖锚点，不作为 skill 检索

## OpenCode 安装布局

```text
.opencode/
├── skills/                 # 顶层 skill；OpenCode 默认自动发现
├── references/             # 外层共享 references/
├── integrations/
└── onescience/             # OneScience 源码快照（非 skill）
```

默认布局下，OpenCode 会自动扫描 `.opencode/skills/*/SKILL.md`，通常**不必**修改 `opencode.jsonc`。

若使用非默认 `--namespace-root`，可在 `opencode.jsonc` 中显式配置：

```jsonc
{
  "skills": {
    "paths": [".opencode/skills"]
  }
}
```

安装器会在 `<namespace_root>/opencode.jsonc.snippet` 生成可合并片段；默认路径为 `.opencode/opencode.jsonc.snippet`。
