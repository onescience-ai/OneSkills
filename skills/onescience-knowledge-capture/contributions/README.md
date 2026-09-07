# Knowledge Contributions

这是 `onescience-knowledge-capture` 的贡献 intake 目录，用于保存经过脱敏的交互经验、知识补充和 skill 集成候选。

目录结构：

```text
contributions/<domain>/<contribution_id>/
  contribution.md
  contribution.json
  issue_payload.json       # 仅在需要 Gitee Issue 时生成
```

这里的内容默认处于 `proposed` 状态，不代表已经进入生产 skill。人工审查时重点检查：

- 事实是否有交互证据支持。
- 候选规则是否写明适用范围、限制和验证状态。
- 是否包含密钥、个人信息、私有路径或未经授权的原始数据。
- 目标是否应迁移到 primitive、expert、executor，还是仅保留为案例。
- 集成建议是否包含契约影响和最小验证计划。

审查通过后，再按 OneSkills 架构将内容迁移到对应 skill 或 `onescience-primitives/assets/`，不要直接把 intake 文档当作已发布知识。
