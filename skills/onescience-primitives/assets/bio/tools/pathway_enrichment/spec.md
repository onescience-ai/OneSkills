# architecture_overview

Pathway enrichment primitive for gene-set selection, ID mapping, over-representation, rank-based enrichment, and interpretation caveats.

This primitive is distilled from the source Agent Skill `pathway-enrichment`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

See the migrated references and the source skill for package-specific dependencies. Install dependencies only in the execution environment that needs them.

# source_knowledge_outline

- Pathway Enrichment
- Overview
- When to Use This Skill
- Choosing the Right Method
- Setup
- gseapy pulls pandas, numpy, scipy, matplotlib. Network access is needed for
- Enrichr, g:Profiler, and MSigDB downloads. For fully offline ORA, use a local
- GMT file with gp.enrich() (see references/gseapy.md).
- Quick Start
- ORA on a hit list (gseapy + Enrichr)

# knowledge_assets

- `references/databases-and-gene-sets.md`: Databases And Gene Sets
- `references/gseapy.md`: Gseapy
- `references/interpretation.md`: Interpretation

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=3, scripts=1, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/pathway-enrichment`.
