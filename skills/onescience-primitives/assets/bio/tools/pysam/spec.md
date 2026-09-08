# architecture_overview

Pysam primitive for SAM/BAM/CRAM/VCF access, read filtering, pileups, coverage summaries, and genomic interval workflows.

This primitive is distilled from the source Agent Skill `pysam`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.8–3.14 and pysam 0.24.0. Bundled scripts use local files. CRAM decoding may require the matching reference FASTA or an explicitly configured REF_PATH/REF_CACHE.

# source_knowledge_outline

- pysam
- Overview
- Installation
- First Decide
- Bundled Scripts
- Coordinate Contract
- The same 100 bases:
- Alignment Files
- Variant Files
- FASTA, FASTQ, and Tabix

# knowledge_assets

- `references/alignment_files.md`: Alignment Files
- `references/api_reference.md`: Api Reference
- `references/common_workflows.md`: Common Workflows
- `references/coordinates_and_indexing.md`: Coordinates And Indexing
- `references/cram_and_performance.md`: Cram And Performance
- `references/migration_to_0_24.md`: Migration To 0 24
- `references/sequence_files.md`: Sequence Files
- `references/sources.md`: Sources
- `references/variant_files.md`: Variant Files

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=9, scripts=4, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/pysam`.
