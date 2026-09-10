# typical_workflow

1. Match the task to `bio.tools.pytdc` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- Research date: 2026-07-23
- PyPI stable: PyTDC 1.1.15, released 2025-03-31
- Package/source repository: mims-harvard/TDC
- PyPI supplies only a source distribution and declares no Requires-Python
- The dependency graph makes CPython 3.11 the reproducible target used here:
- PyTDC imports deprecated pkg_resources at runtime. Setuptools 82 removed that

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.

If `metadata.json.source_payloads` is present, treat those files as preserved migration material only. They can inform future executor design, but they must not be run or imported until promoted through an explicit execution-asset whitelist.
