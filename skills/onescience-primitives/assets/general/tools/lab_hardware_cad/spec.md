# architecture_overview

Lab hardware CAD primitive for fixture design, fabrication planning, parameterized geometry, and inspection-driven iteration.

This primitive is distilled from the source Agent Skill `lab-hardware-cad`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Python 3.10-3.14 with build123d 0.11.1 and matplotlib for snapshots. Geometry commands require build123d; the standards lookup and the interface check run on the standard library alone. No network access needed.

# source_knowledge_outline

- Lab Hardware CAD
- When to use
- Setup
- Required workflow
- 1. Route to a device family
- 2. Establish the interface dimensions before any geometry
- 3. Choose the process before choosing the geometry
- 4. Author a parametric model
- --- INTERFACE (fixed by standard; do not tune) ---
- --- DESIGN (free) ---

# knowledge_assets

- `references/behavior-rigs.md`: Behavior Rigs
- `references/build123d-patterns.md`: Build123D Patterns
- `references/fabrication-limits.md`: Fabrication Limits
- `references/labware-adapters.md`: Labware Adapters
- `references/microfluidics.md`: Microfluidics
- `references/optomechanics.md`: Optomechanics
- `references/validation.md`: Validation

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=7, scripts=4, assets=1. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/lab-hardware-cad`.
