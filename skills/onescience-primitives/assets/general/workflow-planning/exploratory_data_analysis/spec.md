# architecture_overview

Exploratory data analysis primitive for table, sequence, image, and structured scientific datasets, including data profiling, missingness and leakage audits, distribution sensitivity checks, and report scaffolding.

This primitive is distilled from the source Agent Skill `exploratory-data-analysis`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Bundled core CLIs require Python 3.11+ and are local/network-free; the complete pinned optional snapshot requires Python 3.12+, uv, and format-specific libraries listed below.

# source_knowledge_outline

- Exploratory Data Analysis
- Scope and non-negotiable boundary
- Version baseline (verified 2026-07-23)
- Exact capability matrix
- Safe local I/O contract
- Required EDA reasoning
- Workflow
- 1. Confirm authorization and root
- 2. Manifest before content analysis
- 3. Run the narrowest automated tool

# knowledge_assets

- `references/bioinformatics_genomics_formats.md`: Bioinformatics Genomics Formats
- `references/chemistry_molecular_formats.md`: Chemistry Molecular Formats
- `references/general_scientific_formats.md`: General Scientific Formats
- `references/microscopy_imaging_formats.md`: Microscopy Imaging Formats
- `references/proteomics_metabolomics_formats.md`: Proteomics Metabolomics Formats
- `references/spectroscopy_analytical_formats.md`: Spectroscopy Analytical Formats

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=6, scripts=13, assets=1. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/exploratory-data-analysis`.
