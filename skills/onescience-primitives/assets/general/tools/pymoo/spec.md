# architecture_overview

Pymoo primitive for single-, multi-, and many-objective optimization, constraint handling, and algorithm selection planning.

This primitive is distilled from the source Agent Skill `pymoo`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.10+ and pymoo (uv pip install). Optional matplotlib for visualization plots; optional autograd for gradient-based features; optional joblib for JoblibParallelization.

# source_knowledge_outline

- Pymoo - Multi-Objective Optimization in Python
- Overview
- Installation
- When to Use This Skill
- Core Concepts
- The Unified Interface
- Problem Definition Styles
- Problem Types
- Quick Start Workflows
- Algorithm Selection Guide

# knowledge_assets

- `references/algorithms.md`: Algorithms
- `references/constraints_mcdm.md`: Constraints Mcdm
- `references/operators.md`: Operators
- `references/parallelization.md`: Parallelization
- `references/problems.md`: Problems
- `references/quick_start_workflows.md`: Quick Start Workflows
- `references/visualization.md`: Visualization

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=7, scripts=5, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/pymoo`.
