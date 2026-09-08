# architecture_overview

GeoPandas primitive for geospatial tabular data, CRS handling, spatial joins, overlays, geometry validation, and map-ready outputs.

This primitive is distilled from the source Agent Skill `geopandas`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.10+ and uv. Bundled CLIs are local-only; runtime analysis requires the pinned GeoPandas stack below.

# source_knowledge_outline

- GeoPandas
- Reproducible environment
- Safety and privacy contract
- Correctness gates
- CRS and antimeridian rules
- Core API decisions
- Data structures
- Geometry validity, precision, and union
- Joins, overlay, clip, and dissolve
- I/O, Arrow, and PostGIS

# knowledge_assets

- `references/crs-management.md`: Crs Management
- `references/data-io.md`: Data Io
- `references/data-structures.md`: Data Structures
- `references/geometric-operations.md`: Geometric Operations
- `references/spatial-analysis.md`: Spatial Analysis
- `references/visualization.md`: Visualization

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=6, scripts=7, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/geopandas`.
