# typical_workflow

1. Match the task to `general.tools.pylabrobot` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- PyPI stable: PyLabRobot==0.2.1, released 2026-03-23.
- Upstream requirement: Python >=3.9. This skill uses Python 3.11 for its
- /stable/ documentation identifies itself as 0.2.1. /dev/ and repository
- Stable liquid-handler backends include STARBackend, VantageBackend,
- PyLabRobot's GitHub Releases page has no 0.2.x software release entry; use
- Exact device model, installed options, firmware, computer/OS, and transport.

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.
