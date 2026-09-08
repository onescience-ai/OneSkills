# architecture_overview

FluidSim primitive for fluid simulation setup, solver selection, parameter planning, diagnostics, and reproducible run organization.

This primitive is distilled from the source Agent Skill `fluidsim`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Bundled CLIs require Python 3.11+ and use the standard library; HDF5/netCDF4 metadata tools lazily use h5py when available. Simulation examples target fluidsim 0.9.0, fluidfft 0.4.5, and pyFFTW 0.15.1. MPI/native FFT use requires a site-compatible MPI implementation, development headers, FFTW/PFFT/P3DFFT libraries, compilers, and an approved scheduler workflow. No GPU backend is assumed.

# source_knowledge_outline

- FluidSim
- Required workflow
- Version and installation
- API snapshot
- Solvers
- Forcing and time advancement
- Outputs, loading, and restart
- Scientific acceptance gate
- Bundled local tools
- References

# knowledge_assets

- `references/advanced_features.md`: Advanced Features
- `references/installation.md`: Installation
- `references/output_analysis.md`: Output Analysis
- `references/parameters.md`: Parameters
- `references/simulation_workflow.md`: Simulation Workflow
- `references/solvers.md`: Solvers

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=6, scripts=9, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/fluidsim`.
