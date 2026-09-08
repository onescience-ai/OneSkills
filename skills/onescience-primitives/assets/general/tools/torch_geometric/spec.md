# architecture_overview

PyTorch Geometric primitive for graph data, heterogeneous graphs, GNN layers, and graph-learning workflows.

This primitive is distilled from the source Agent Skill `torch-geometric`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.10+, PyTorch 2.6+, and torch-geometric 2.7.x. Optional extension wheels (pyg-lib, torch-scatter, torch-sparse, torch-cluster) must match your PyTorch/CUDA build from https://data.pyg.org/whl.

# source_knowledge_outline

- PyTorch Geometric (PyG)
- Installation
- 1. Install PyTorch first (match your CUDA/CPU setup — see https://pytorch.org/get-started/locally/)
- 2. Core PyG (no extension wheels required for basic usage)
- Then install wheels for your torch+CUDA combo, e.g.:
- PyG 2.7 notes
- Core Concepts
- Graph Data: `Data` and `HeteroData
- If edges are [[src1, dst1], [src2, dst2], ...] — transpose first:
- Datasets

# knowledge_assets

- `references/custom_datasets.md`: Custom Datasets
- `references/explainability.md`: Explainability
- `references/heterogeneous.md`: Heterogeneous
- `references/link_prediction.md`: Link Prediction
- `references/message_passing.md`: Message Passing
- `references/scaling.md`: Scaling

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=6, scripts=0, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/torch-geometric`.
