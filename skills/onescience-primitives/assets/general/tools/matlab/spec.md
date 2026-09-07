# architecture_overview

MATLAB and GNU Octave primitive for numerical workflows, arrays, tabular and time data, tests, projects, graphics, MAT files, and Python interoperability planning.

This primitive is distilled from the source Agent Skill `matlab`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

>-

# source_knowledge_outline

- MATLAB and GNU Octave
- Product and license gate
- Nonnegotiable safety boundary
- Default workflow
- Language and data checklist
- Scripts, functions, and live scripts
- Arrays, indexing, and numerics
- Tables, timetables, and missing values
- Graphics and export
- MAT files and exchange

# knowledge_assets

- `references/data-import-export.md`: Data Import Export
- `references/executing-scripts.md`: Executing Scripts
- `references/graphics-visualization.md`: Graphics Visualization
- `references/mathematics.md`: Mathematics
- `references/matrices-arrays.md`: Matrices Arrays
- `references/octave-compatibility.md`: Octave Compatibility
- `references/programming.md`: Programming
- `references/python-integration.md`: Python Integration

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=8, scripts=8, assets=3. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/matlab`.
