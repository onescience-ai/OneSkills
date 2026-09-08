# architecture_overview

Bulk RNA-seq workflow primitive for count matrices, metadata, QC, differential expression, enrichment, and reporting.

This primitive is distilled from the source Agent Skill `bulk-rnaseq`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

See the migrated references and the source skill for package-specific dependencies. Install dependencies only in the execution environment that needs them.

# source_knowledge_outline

- Bulk RNA-seq
- Overview
- When to Use This Skill
- The Pipeline at a Glance
- Two Upstream Paths — Pick One
- Setup
- This skill's glue (bridge + handoffs) — Python
- Downstream skills install their own deps:
- pydeseq2 skill           -> uv pip install pydeseq2
- pathway-enrichment skill -> uv pip install gseapy gprofiler-official

# knowledge_assets

- `references/counts-and-handoff.md`: Counts And Handoff
- `references/design-and-qc.md`: Design And Qc
- `references/upstream-manual.md`: Upstream Manual
- `references/upstream-nfcore.md`: Upstream Nfcore

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=4, scripts=2, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/bulk-rnaseq`.
