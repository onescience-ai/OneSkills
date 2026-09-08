# typical_workflow

1. Match the task to `general.tools.lab_hardware_cad` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- the source of the dimension: a published standard, a vendor drawing, or a user measurement;
- the nominal value and tolerance;
- the clearance or interference you intend, and why.
- Every dimension that a user might change is a module-level named constant with units in the
- Expose build() -> Part. gen.py calls it.
- Group parameters into an INTERFACE block (dimensions fixed by a standard, annotated with the

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.
