# typical_workflow

1. Match the task to `general.tools.uncertainty_and_units` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- converting between units, including conversions that need a physical context
- propagating uncertainty through a measurement model, with or without correlated inputs;
- building a GUM uncertainty budget from calibration certificates, specifications, and
- choosing a coverage factor and deciding whether k = 2 is defensible;
- rounding and writing a result so a reader knows what the ± means;
- extracting parameter uncertainties from a curve fit without discarding correlations;

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.
