# architecture_overview

PyLabRobot primitive for lab-automation resources, liquid-handling plans, offline simulation, resource trees, and supported-device integrations.

This primitive is distilled from the source Agent Skill `pylabrobot`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Verified against PyLabRobot 0.2.1 on Python 3.9+. Bundled planning CLIs require only Python 3.11+ and make no serial, USB, or network connections. Physical devices need model-specific extras, configuration, calibration, and trained operator approval.

# source_knowledge_outline

- PyLabRobot
- Verified snapshot
- Non-negotiable hardware boundary
- Required intake
- Reproducible install
- Offline-first workflow
- Verified software-only example
- API rules that prevent stale code
- References
- Dated upstream sources

# knowledge_assets

- `references/analytical-equipment.md`: Analytical Equipment
- `references/hardware-backends.md`: Hardware Backends
- `references/liquid-handling.md`: Liquid Handling
- `references/material-handling.md`: Material Handling
- `references/resources.md`: Resources
- `references/visualization.md`: Visualization

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=6, scripts=7, assets=1. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/pylabrobot`.
