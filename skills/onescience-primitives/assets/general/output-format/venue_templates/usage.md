# typical_workflow

1. Match the task to `general.output-format.venue_templates` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- a verification-first workflow for current venue rules;
- bundled LaTeX scaffolds for a small, explicit set of document types;
- writing-style and reviewer-expectation guides; and
- local helpers for discovering, copying, and inspecting templates.
- locating official journal or conference author instructions;
- checking page limits, required sections, anonymity, supplemental-material rules, or citation style;

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.
