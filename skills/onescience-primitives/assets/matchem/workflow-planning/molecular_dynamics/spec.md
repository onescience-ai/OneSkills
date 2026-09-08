# architecture_overview

Molecular dynamics planning primitive for force-field selection, system preparation, equilibration, production, analysis, and reproducibility checks.

This primitive is distilled from the source Agent Skill `molecular-dynamics`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

See the migrated references and the source skill for package-specific dependencies. Install dependencies only in the execution environment that needs them.

# source_knowledge_outline

- Molecular Dynamics
- Overview
- or
- When to Use This Skill
- Core Workflow: OpenMM Simulation
- 1. System Preparation
- 2. Energy Minimization
- 3. NVT Equilibration
- 4. NPT Equilibration and Production
- Trajectory Analysis with MDAnalysis

# knowledge_assets

- `references/mdanalysis_analysis.md`: Mdanalysis Analysis

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=1, scripts=0, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/molecular-dynamics`.
