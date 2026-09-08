# typical_workflow

1. Match the task to `bio.tools.geniml` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- Latest stable PyPI release on 2026-07-23: geniml==0.8.4 (2026-01-14).
- PyPI does not declare Requires-Python; its classifiers list Python
- geniml==0.8.4 accepts gtars>=0.2.5; the verified base smoke used current
- Extras are ml and test. The base install omits Torch, Gensim, Scanpy,
- Upstream documentation contains stale examples. Release source and installed
- assembly and patch/accession where possible (for example GRCh38 versus

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.
