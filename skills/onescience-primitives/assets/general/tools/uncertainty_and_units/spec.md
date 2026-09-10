# architecture_overview

Uncertainty-and-units primitive for unit conversion, dimensional checking, uncertainty propagation, GUM budgets, coverage factors, and plausibility auditing of scientific calculations.

This primitive is distilled from the source Agent Skill `uncertainty-and-units`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.12+. The numeric CLIs need pint, uncertainties, NumPy, and SciPy; the static auditor is standard-library only. All bundled tooling runs locally with no network access.

# source_knowledge_outline

- Uncertainty and units
- Scope
- Current release and installation
- Non-negotiable workflow
- The failures this skill exists to prevent
- A unit stripped at an unknown scale
- Offset temperature arithmetic
- Logarithmic units that add by multiplying
- A correlation destroyed by a round trip
- A covariance matrix silently rescaled

# knowledge_assets

- `references/domain-conversions.md`: Domain Conversions
- `references/gum-methodology.md`: Gum Methodology
- `references/pint-recipes.md`: Pint Recipes
- `references/plausibility-scales.md`: Plausibility Scales
- `references/reporting-rules.md`: Reporting Rules
- `references/uncertainties-recipes.md`: Uncertainties Recipes

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=6, scripts=7, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/uncertainty-and-units`.
