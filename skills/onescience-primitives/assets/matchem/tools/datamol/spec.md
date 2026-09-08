# architecture_overview

Datamol cheminformatics utility primitive for molecule standardization, scaffold handling, descriptors, clustering, and dataset preparation.

This primitive is distilled from the source Agent Skill `datamol`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.8+ and datamol (uv pip install). RDKit is installed automatically as a datamol dependency (since 0.12.2). Optional s3fs/gcsfs for cloud I/O via fsspec.

# source_knowledge_outline

- Datamol Cheminformatics Skill
- Overview
- Installation and Setup
- Core Workflows
- Parallelization
- Reference Documentation
- Best Practices
- Error Handling
- Safe molecule creation
- Safe batch processing

# knowledge_assets

- `references/conformers_module.md`: Conformers Module
- `references/core_api.md`: Core Api
- `references/core_workflows.md`: Core Workflows
- `references/descriptors_viz.md`: Descriptors Viz
- `references/fragments_scaffolds.md`: Fragments Scaffolds
- `references/io_module.md`: Io Module
- `references/reactions_data.md`: Reactions Data
- `references/workflow_patterns.md`: Workflow Patterns

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=8, scripts=0, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/datamol`.
