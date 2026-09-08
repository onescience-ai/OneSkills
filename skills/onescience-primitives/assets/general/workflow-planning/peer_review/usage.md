# typical_workflow

1. Match the task to `general.workflow-planning.peer_review` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- Send unpublished manuscript, supplement, review, or editorial text to an external service without specific publisher/author authorization and venue permission
- Upload confidential content to a public model, search engine, citation service, grammar tool, plagiarism checker, or image service
- Reuse content for training, benchmarking, product improvement, or unrelated research
- Read broad environment state, .env files, API keys, or credentials
- Call a network, LLM, or image API from bundled tools
- Invoke another skill or a PDF/image pipeline automatically

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.
