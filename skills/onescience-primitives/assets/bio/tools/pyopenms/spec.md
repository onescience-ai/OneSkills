# architecture_overview

pyOpenMS mass-spectrometry primitive for feature finding, alignment, identification, quantification, and proteomics workflow planning.

This primitive is distilled from the source Agent Skill `pyopenms`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.9+ and uv. Examples and scripts target pyOpenMS 3.5.0.

# source_knowledge_outline

- PyOpenMS
- Overview
- Installation
- Scripts (start here)
- Inspect & convert
- Feature detection & quantification
- Annotation
- Identification
- Chemistry
- Targeted & visualization

# knowledge_assets

- `references/data_structures.md`: Data Structures
- `references/feature_detection.md`: Feature Detection
- `references/file_io.md`: File Io
- `references/identification.md`: Identification
- `references/metabolomics.md`: Metabolomics
- `references/signal_processing.md`: Signal Processing

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=6, scripts=16, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/pyopenms`.
