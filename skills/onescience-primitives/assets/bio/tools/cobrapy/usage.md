# typical_workflow

1. Match the task to `bio.tools.cobrapy` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- Loading, building, or exporting genome-scale metabolic models (SBML, JSON, YAML)
- Running FBA, pFBA, FVA, or flux sampling on COBRA models
- Performing gene or reaction knockout screens and production envelope analysis
- Designing or optimizing growth media and exchange constraints
- Gap-filling infeasible models or validating model consistency
- Irreversible: lower_bound = 0, upper_bound > 0

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.
