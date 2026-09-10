# typical_workflow

1. Match the task to `bio.tools.gtars` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- Python: [gtars==0.9.2](https://pypi.org/project/gtars/), released
- Rust meta-crate: [gtars=0.9.0](https://crates.io/crates/gtars), released
- CLI crate/binary: [gtars-cli=0.9.0](https://crates.io/crates/gtars-cli);
- Direct refget crate: [gtars-refget=0.9.1](https://crates.io/crates/gtars-refget),
- Upstream intentionally versions workspace crates, Python bindings, and CLI
- The published docs changelog stops at 0.5.1. API examples here were checked

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.

If `metadata.json.source_payloads` is present, treat those files as preserved migration material only. They can inform future executor design, but they must not be run or imported until promoted through an explicit execution-asset whitelist.
