# architecture_overview

NetworkX primitive for graph construction, graph algorithms, network metrics, traversal, and reproducible graph-analysis workflows.

This primitive is distilled from the source Agent Skill `networkx`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

See the migrated references and the source skill for package-specific dependencies. Install dependencies only in the execution environment that needs them.

# source_knowledge_outline

- NetworkX
- Overview
- When to Use This Skill
- Core Capabilities
- 1. Graph Creation and Manipulation
- Create empty graph
- Add nodes (can be any hashable type)
- Add edges
- 2. Graph Algorithms
- Find shortest path

# knowledge_assets

- `references/algorithms.md`: Algorithms
- `references/generators.md`: Generators
- `references/graph-basics.md`: Graph Basics
- `references/io.md`: Io
- `references/visualization.md`: Visualization

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=5, scripts=0, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/networkx`.
