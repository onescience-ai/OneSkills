# architecture_overview

MatchMS primitive for mass-spectrometry spectrum processing, metadata cleaning, similarity scoring, and metabolomics library matching.

This primitive is distilled from the source Agent Skill `matchms`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python >=3.10,<3.15, uv, and matchms 0.33.1. Local file workflows need no credentials; metabolomics-USI loading requires network access.

# source_knowledge_outline

- Matchms
- Purpose and Scope
- Install the Verified Release
- Operating Workflow
- Current API Guardrails
- Quick Start: Clean and Search a Library
- Pair Scoring
- Choose a Similarity Method
- Large Comparisons
- Bundled Library-Search CLI

# knowledge_assets

- `references/filtering.md`: Filtering
- `references/importing_exporting.md`: Importing Exporting
- `references/migration.md`: Migration
- `references/similarity.md`: Similarity
- `references/sources.md`: Sources
- `references/workflows.md`: Workflows

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=6, scripts=1, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/matchms`.
