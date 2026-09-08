# architecture_overview

Pymatgen materials-science primitive for crystal structures, compositions, transformations, phase diagrams, and VASP-oriented workflows.

This primitive is distilled from the source Agent Skill `pymatgen`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Python 3.11+ with uv. The verified snapshot uses pymatgen 2026.5.4, pymatgen-core 2026.7.16, and mp-api 0.46.4. Bundled help and planning CLIs use only the standard library; local scientific execution lazily requires the pinned pymatgen packages. Materials Project access additionally requires explicit network approval and the single named secret MP_API_KEY.

# source_knowledge_outline

- pymatgen
- Verified snapshot (2026-07-23)
- Required workflow
- Core objects
- Safe local structure intake
- Symmetry
- Conversion and parser/writer I/O
- Transformations and provenance
- Local phase diagrams
- Band structures, DOS, VASP, and Q-Chem

# knowledge_assets

- `references/analysis_modules.md`: Analysis Modules
- `references/core_classes.md`: Core Classes
- `references/io_formats.md`: Io Formats
- `references/materials_project_api.md`: Materials Project Api
- `references/transformations_workflows.md`: Transformations Workflows

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=5, scripts=9, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/pymatgen`.
