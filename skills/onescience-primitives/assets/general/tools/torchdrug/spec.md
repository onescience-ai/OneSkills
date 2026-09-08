# architecture_overview

TorchDrug primitive for molecular deep learning, graph learning, pretraining, generation, and knowledge-graph tasks.

This primitive is distilled from the source Agent Skill `torchdrug`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

TorchDrug 0.2.1 requires Python 3.7-3.10 and supports PyTorch 1.8-2.0. Apple Silicon is CPU-only; MPS is unsupported.

# source_knowledge_outline

- TorchDrug
- Start with the version guard
- Installation
- Canonical property-prediction workflow
- Choose the official workflow
- Molecular property prediction
- Self-supervised molecular pretraining
- Molecule generation
- Retrosynthesis
- Knowledge graph reasoning

# knowledge_assets

- `references/core_concepts.md`: Core Concepts
- `references/datasets.md`: Datasets
- `references/knowledge_graphs.md`: Knowledge Graphs
- `references/models_architectures.md`: Models Architectures
- `references/molecular_generation.md`: Molecular Generation
- `references/molecular_property_prediction.md`: Molecular Property Prediction
- `references/protein_modeling.md`: Protein Modeling
- `references/retrosynthesis.md`: Retrosynthesis

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=8, scripts=0, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/torchdrug`.
