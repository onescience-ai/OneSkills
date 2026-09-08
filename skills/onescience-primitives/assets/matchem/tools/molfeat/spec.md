# architecture_overview

Molfeat primitive for molecular featurization, fingerprints, embeddings, and chemical machine-learning feature pipelines.

This primitive is distilled from the source Agent Skill `molfeat`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.9–3.10 (molfeat 0.11.0 does not support 3.11+). Requires datamol, PyTorch, and optional extras for GNN/transformer models.

# source_knowledge_outline

- Molfeat - Molecular Featurization Hub
- Overview
- When to Use This Skill
- Installation
- With all pip-installable optional dependencies
- Core Concepts
- 1. Calculators (`molfeat.calc`)
- 2. Transformers (`molfeat.trans`)
- 3. Pretrained Transformers (`molfeat.trans.pretrained`)
- Quick Start Workflow

# knowledge_assets

- `references/api_reference.md`: Api Reference
- `references/available_featurizers.md`: Available Featurizers
- `references/choosing_a_featurizer.md`: Choosing A Featurizer
- `references/examples.md`: Examples

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=4, scripts=0, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/molfeat`.
