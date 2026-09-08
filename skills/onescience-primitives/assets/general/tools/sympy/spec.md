# architecture_overview

SymPy primitive for symbolic mathematics, algebra, calculus, equation solving, code generation, and exact analytical derivations.

This primitive is distilled from the source Agent Skill `sympy`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.9+ and SymPy 1.14+. Optional NumPy/SciPy/Matplotlib for lambdify examples; C/Fortran compiler for autowrap/codegen.

# source_knowledge_outline

- SymPy - Symbolic Mathematics in Python
- Overview
- Installation
- Install SymPy using uv
- Optional: for lambdify and plotting examples
- When to Use This Skill
- Core Capabilities
- Working with SymPy: Best Practices
- 1. Always Define Symbols First
- Now x, y, z can be used in expressions

# knowledge_assets

- `references/advanced-topics.md`: Advanced Topics
- `references/code-generation-printing.md`: Code Generation Printing
- `references/core-capabilities.md`: Core Capabilities
- `references/core_capabilities.md`: Core Capabilities
- `references/matrices-linear-algebra.md`: Matrices Linear Algebra
- `references/physics-mechanics.md`: Physics Mechanics

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=6, scripts=0, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/sympy`.
