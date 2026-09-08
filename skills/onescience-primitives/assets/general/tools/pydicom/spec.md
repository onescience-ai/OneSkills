# architecture_overview

pydicom primitive for DICOM inspection, metadata extraction, pixel-data planning, de-identification, and medical-imaging workflows.

This primitive is distilled from the source Agent Skill `pydicom`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Python 3.10+ with pydicom 3.0.2; optional pinned NumPy, Pillow, and pixel plugins. Helper CLIs are local-only and require authorized data.

# source_knowledge_outline

- pydicom
- Mandatory safety boundary
- Installation
- JPEG/JPEG-LS, JPEG 2000/HTJ2K, and faster RLE through pylibjpeg
- JPEG-LS encoder/decoder
- Alternative decoder with platform-specific wheels
- Choose the workflow
- Read datasets safely
- Dataset, DataElement, and sequences
- Add all attributes required by the selected IOD before writing.

# knowledge_assets

- `references/common_tags.md`: Common Tags
- `references/transfer_syntaxes.md`: Transfer Syntaxes

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=2, scripts=10, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/pydicom`.
