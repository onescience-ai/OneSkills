# architecture_overview

COBRApy primitive for constraint-based metabolic modeling, flux balance analysis, reaction rules, and growth-media workflows.

This primitive is distilled from the source Agent Skill `cobrapy`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.9+ (cobra 0.30+ dropped 3.8). Install with uv pip install. GLPK (swiglpk) is the default solver; CPLEX/Gurobi optional. load_model fetches from bundled data, BiGG, or BioModels (network required for remote models).

# source_knowledge_outline

- COBRApy - Constraint-Based Reconstruction and Analysis
- Overview
- When to Use This Skill
- Installation
- Core Capabilities
- 1. Model Management
- Bundled locally (no network): textbook, iJO1366, salmonella
- Remote (BiGG / BioModels; requires network, cached after first fetch)
- Load from files
- 2. Model Structure and Components

# knowledge_assets

- `references/api_quick_reference.md`: Api Quick Reference
- `references/workflows.md`: Workflows

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=2, scripts=0, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/cobrapy`.
