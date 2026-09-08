# typical_workflow

1. Match the task to `bio.tools.pathml` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- Installable stable release: PyPI pathml==3.0.5, published 2026-03-24.
- The v3.0.5 release notes state Python 3.10-3.12 and sunset 3.9.
- GitHub releases v3.0.6 (2026-04-14) and v3.0.7 (2026-07-09) exist, but PyPI has
- ReadTheDocs /latest identifies itself as 3.0.5. Examples here were checked
- This skill is MIT-licensed. PathML itself is GPL-2.0 with upstream commercial
- SegmentMIFRemote downloads an ONNX file from

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.
