# architecture_overview

gget primitive for fast bioinformatics database lookups including gene information, BLAST or BLAT, viral sequence downloads, AlphaFold structures, enrichment analysis, and OpenTargets queries.

This primitive is distilled from the source Agent Skill `gget`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python >=3.8 and gget 0.30.5-compatible APIs. Optional setup modules may install scientific dependencies that lag the newest Python releases; use Python 3.9 or 3.10 if `gget setup cellxgene` or `gget setup alphafold` fails.

# source_knowledge_outline

- gget
- Overview
- Installation
- Reproducible install targeting this skill
- In Python/Jupyter
- Quick Start
- Command-line
- Python
- Module Categories
- Common Workflows

# knowledge_assets

- `references/common_workflows.md`: Common Workflows
- `references/database_info.md`: Database Info
- `references/module_catalog.md`: Module Catalog
- `references/module_reference.md`: Module Reference
- `references/workflows.md`: Workflows

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=5, scripts=3, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/gget`.
