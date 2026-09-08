# architecture_overview

scikit-survival primitive for censored-data analysis, survival modeling, competing risks, and reproducible evaluation planning.

This primitive is distilled from the source Agent Skill `scikit-survival`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.11+, uv, and the pinned scikit-survival 0.28.0 stack for executable examples. Bundled CLIs are local and network-free by default.

# source_knowledge_outline

- scikit-survival
- Scope
- Current release and installation
- Non-negotiable workflow
- Outcome construction
- Equivalent for pandas or Polars:
- Leakage-safe pipeline
- Model choice
- Prediction and metric contracts
- Pipelines, metadata routing, and tuning

# knowledge_assets

- `references/competing-risks.md`: Competing Risks
- `references/cox-models.md`: Cox Models
- `references/data-handling.md`: Data Handling
- `references/ensemble-models.md`: Ensemble Models
- `references/evaluation-metrics.md`: Evaluation Metrics
- `references/svm-models.md`: Svm Models

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=6, scripts=6, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/scikit-survival`.
