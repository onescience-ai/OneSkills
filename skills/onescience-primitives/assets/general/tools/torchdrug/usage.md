# typical_workflow

1. Match the task to `general.tools.torchdrug` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- Apple Silicon: PyTorch 1.13 or later, CPU only; no MPS support
- Dataset: datasets.ClinTox, BBBP, Tox21, QM9, or another documented
- Model: start with models.GIN; use edge_input_dim when the selected feature
- Task: tasks.PropertyPrediction.
- Read [molecular property prediction](references/molecular_property_prediction.md).
- InfoGraph: models.InfoGraph(gin_model, separate_model=False) wrapped by

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.
