# architecture_overview

Astropy primitive for astronomy tables, units, coordinates, FITS files, time handling, and observation-data workflows.

This primitive is distilled from the source Agent Skill `astropy`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.11+ with astropy installed (uv for package installation). Some features (object name resolution, site lookups, remote FITS reads, IERS updates) need network access.

# source_knowledge_outline

- Astropy
- Overview
- When to Use This Skill
- Quick Start
- Units and quantities
- Coordinates
- Time
- FITS files
- Tables
- Cosmology

# knowledge_assets

- `references/coordinates.md`: Coordinates
- `references/cosmology.md`: Cosmology
- `references/fits.md`: Fits
- `references/tables.md`: Tables
- `references/time.md`: Time
- `references/units.md`: Units
- `references/wcs_and_other_modules.md`: Wcs And Other Modules

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=7, scripts=0, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/astropy`.
