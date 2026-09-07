# architecture_overview

Qiskit primitive for quantum circuits, target-aware transpilation, V2 primitives, local or noisy simulation, IBM QPU execution, Runtime sessions, and error mitigation planning.

This primitive is distilled from the source Agent Skill `qiskit`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Python 3.10+ on a supported 64-bit platform. Local SDK workflows need qiskit; noisy simulation needs qiskit-aer; IBM QPU access needs qiskit-ibm-runtime, network access, an IBM Quantum Platform account, and an API key.

# source_knowledge_outline

- Qiskit
- Choose the Right Path
- Installation
- Core SDK plus plotting support
- Add only when needed
- Core Workflow
- Quick Local Sampling
- Quick Local Estimation
- IBM QPU Sampling
- IBM QPU Estimation

# knowledge_assets

- `references/algorithms.md`: Algorithms
- `references/backends.md`: Backends
- `references/circuits.md`: Circuits
- `references/migration.md`: Migration
- `references/patterns.md`: Patterns
- `references/primitives.md`: Primitives
- `references/setup.md`: Setup
- `references/sources.md`: Sources
- `references/testing.md`: Testing
- `references/transpilation.md`: Transpilation
- `references/visualization.md`: Visualization

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=11, scripts=3, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/qiskit`.
