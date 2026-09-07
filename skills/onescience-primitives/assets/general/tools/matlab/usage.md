# typical_workflow

1. Match the task to `general.tools.matlab` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- MATLAB R2026a is proprietary. Do not assume MATLAB, MATLAB Online, a
- MATLAB Runtime is not MATLAB. It runs compatible applications produced
- GNU Octave 11.3.0 is free software under GPLv3+. Octave packages are not
- Ask which runtime, release, platform, installed products, and license context
- eval, evalin, assignin, text-derived feval, str2func, callbacks,
- system, unix, dos, shell escape !, Java, .NET, Python (py.*,

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.
