# architecture_overview

Arboreto primitive for gene regulatory network inference with GRNBoost2 and GENIE3, scalable Dask execution, and transcriptomics workflows.

This primitive is distilled from the source Agent Skill `arboreto`. It is a planning and retrieval primitive. Preserved source payloads, if present, are inert copies for review and later binding; they are not executable runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

See the migrated references and the source skill for package-specific dependencies. Install dependencies only in the execution environment that needs them.

# source_knowledge_outline

- Arboreto
- Overview
- Quick Start
- Core Capabilities
- 1. Basic GRN Inference
- 2. Algorithm Selection
- Fast, recommended
- Classic algorithm
- 3. Distributed Computing
- Installation

# knowledge_assets

- `references/algorithms.md`: Algorithms
- `references/basic_inference.md`: Basic Inference
- `references/distributed_computing.md`: Distributed Computing

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# source_payloads

- `source_payload/scripts/basic_grn_inference.py` (source_script): Basic Grn Inference

Source payloads are indexed in `metadata.json.source_payloads` with SHA-256 values. They preserve source scripts, templates, and static files for later migration review, but they do not grant execution permission.

# execution_policy

No source scripts were promoted as execution assets in this batch. Source-side file counts were: references=3, scripts=1, assets=0. Preserved source payloads remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/arboreto`.
