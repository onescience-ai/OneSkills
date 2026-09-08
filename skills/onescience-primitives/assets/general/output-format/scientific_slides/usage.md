# typical_workflow

1. Match the task to `general.output-format.scientific_slides` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- Compelling visuals: High-quality figures, images, diagrams (not just bullet points)
- Research context: Proper citations from research-lookup establishing credibility
- Minimal text: Bullet points as prompts, YOU provide the explanation verbally
- Professional design: Modern color schemes, strong visual hierarchy, generous white space
- Story-driven: Clear narrative arc, not just data dumps
- Preparing conference presentations (5-20 minutes)

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.
