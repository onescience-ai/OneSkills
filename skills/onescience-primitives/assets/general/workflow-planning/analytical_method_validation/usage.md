# typical_workflow

1. Match the task to `general.workflow-planning.analytical_method_validation` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- Precision is estimated within each level, never pooled across levels. Pooling 80/100/120%
- --require-ci-within-limit enforces that the whole confidence interval sits inside the
- "p > 0.05, no significant difference, therefore the methods are equivalent." Failing to
- Ordinary least squares for method comparison. OLS assumes the reference values carry no
- references/framework-selection.md — which framework governs, and the questions that decide it
- references/ich-q2r2.md — structure, Table 1 and Table 2, per-characteristic recommended data

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.
