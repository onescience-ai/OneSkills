# architecture_overview

QuTiP primitive for quantum object construction, open-system dynamics, steady states, spectra, and solver planning.

This primitive is distilled from the source Agent Skill `qutip`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.11+, uv, and qutip==5.3.0 for executable simulations. Bundled planners and all script help run with the Python standard library; plotting requires the pinned graphics extra. No network service or credentials are used.

# source_knowledge_outline

- QuTiP 5
- Scope
- Reproducible uv snapshot
- Non-negotiable model contract
- Qobj, dimensions, and tensor order
- Choose the solver by physics
- Deterministic open-system example
- Time-dependent systems
- Trajectories and stochastic solvers
- Steady states, spectra, and phase space

# knowledge_assets

- `references/advanced.md`: Advanced
- `references/analysis.md`: Analysis
- `references/core_concepts.md`: Core Concepts
- `references/time_evolution.md`: Time Evolution
- `references/visualization.md`: Visualization

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=5, scripts=7, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/qutip`.
