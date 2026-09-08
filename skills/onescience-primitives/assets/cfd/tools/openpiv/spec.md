# architecture_overview

OpenPIV primitive for particle image velocimetry workflows, velocity-field extraction, validation, scaling, and visualization planning.

This primitive is distilled from the source Agent Skill `openpiv`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.10+ with openpiv installed (uv pip install openpiv). numpy, scipy, scikit-image, and matplotlib arrive as dependencies. No network access needed after install.

# source_knowledge_outline

- OpenPIV
- Overview
- When to use
- Quick Start
- Pin it when the analysis needs to be reproducible -- this is the version every
- snippet below was checked against.
- Cross-correlate. Returns (u, v, s2n) whenever sig2noise_method is not None.
- flags is a boolean array: True marks a spurious vector.
- Scale to physical units, then flip to image coordinates for plotting.
- Core Concepts

# knowledge_assets

- `references/advanced_algorithms.md`: Advanced Algorithms

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=1, scripts=4, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/openpiv`.
