# architecture_overview

SHAP primitive for model explanation, masker selection, additivity checks, multi-output attributions, and local or global attribution plots.

This primitive is distilled from the source Agent Skill `shap`. It is a planning and retrieval primitive. Preserved source payloads, if present, are inert copies for review and later binding; they are not executable runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.12+ and uv for SHAP 0.52.0; model-specific libraries are optional.

# source_knowledge_outline

- SHAP
- Operating Rules
- Install
- Standard Workflow
- 1. Define the explanation target
- 2. Select an explainer and masker
- 3. Compute a modern `Explanation
- sklearn tree classifiers expose one output per class.
- 4. Control tree output semantics when needed
- 5. Use a model-agnostic callable deliberately

# knowledge_assets

- `references/data-maskers.md`: Data Maskers
- `references/explainers.md`: Explainers
- `references/migration.md`: Migration
- `references/modalities.md`: Modalities
- `references/plots.md`: Plots
- `references/theory.md`: Theory
- `references/troubleshooting.md`: Troubleshooting
- `references/workflows.md`: Workflows

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# source_payloads

- `source_payload/scripts/tabular_report.py` (source_script): Tabular Report

Source payloads are indexed in `metadata.json.source_payloads` with SHA-256 values. They preserve source scripts, templates, and static files for later migration review, but they do not grant execution permission.

# execution_policy

No source scripts were promoted as execution assets in this batch. Source-side file counts were: references=8, scripts=1, assets=0. Preserved source payloads remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/shap`.
