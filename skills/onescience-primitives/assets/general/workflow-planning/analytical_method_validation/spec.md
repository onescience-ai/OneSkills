# architecture_overview

Analytical method validation primitive for planning, executing, and documenting validation, verification, transfer, and comparison of assays under ICH Q2(R2), Q14, USP, ICH M10, CLSI EP, and ISO/IEC 17025.

This primitive is distilled from the source Agent Skill `analytical-method-validation`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.11+. Scripts use only the standard library - no numpy, scipy, or network access. Statistical distributions are computed from first principles so results are reproducible in any conforming interpreter.

# source_knowledge_outline

- Analytical Method Validation
- When to use
- The two rules
- Scope
- Copyright boundary
- Frameworks
- Scripts
- Workflow
- 1. Fix the framework and the required characteristics
- 2. Generate the protocol and fill in the criteria

# knowledge_assets

- `references/compendial-and-clsi.md`: Compendial And Clsi
- `references/framework-selection.md`: Framework Selection
- `references/ich-m10-bioanalytical.md`: Ich M10 Bioanalytical
- `references/ich-q2r2.md`: Ich Q2R2
- `references/source-ledger.md`: Source Ledger
- `references/statistics.md`: Statistics

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=6, scripts=8, assets=2. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/analytical-method-validation`.
