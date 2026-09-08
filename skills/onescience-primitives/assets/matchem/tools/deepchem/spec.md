# architecture_overview

DeepChem primitive for molecular machine learning datasets, featurization, model training, evaluation, and uncertainty-aware chemical prediction.

This primitive is distilled from the source Agent Skill `deepchem`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.7–3.11 (PyPI 2.8.0 caps at <3.12). Install PyTorch, TensorFlow, or JAX before the matching deepchem extra. RDKit is a core dependency.

# source_knowledge_outline

- DeepChem
- Overview
- When to Use This Skill
- Core Capabilities
- Example Scripts
- 1. `predict_solubility.py
- Use Delaney benchmark
- Use custom data
- 2. `graph_neural_network.py
- Train GCN on Tox21

# knowledge_assets

- `references/api_reference.md`: Api Reference
- `references/core_capabilities.md`: Core Capabilities
- `references/typical_workflows.md`: Typical Workflows
- `references/workflows.md`: Workflows

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=4, scripts=3, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/deepchem`.
