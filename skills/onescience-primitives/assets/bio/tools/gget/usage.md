# typical_workflow

1. Match the task to `bio.tools.gget` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- Command-line: JSON (default) or CSV with -csv flag
- Python: DataFrame or dictionary
- -o/--out: Save results to file
- -q/--quiet: Suppress progress information
- -csv: Return CSV format (command-line only)
- Use --limit to control result sizes for large queries

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.
