# architecture_overview

TileDB-VCF primitive for variant storage, region queries, population-genomics access, and cloud-backed genomics data workflows.

This primitive is distilled from the source Agent Skill `tiledbvcf`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

See the migrated references and the source skill for package-specific dependencies. Install dependencies only in the execution environment that needs them.

# source_knowledge_outline

- TileDB-VCF
- Overview
- When to Use This Skill
- Quick Start
- Installation
- Enter the following two lines if you are on a M1 Mac
- Create the conda environment
- Mamba is a faster and more reliable alternative to conda
- Install TileDB-Py and TileDB-VCF, align with other useful libraries
- Basic Examples

# knowledge_assets

- No reference files were bundled in the source skill.

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=0, scripts=0, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/tiledbvcf`.
