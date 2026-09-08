# architecture_overview

Genomic coordinate primitive for intervals, genome builds, BED-like data, coordinate validation, liftover planning, and overlap semantics.

This primitive is distilled from the source Agent Skill `genomic-coordinates`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.11+. Scripts use only the standard library - no third-party packages and no network access. Variant normalisation needs a reference FASTA, and uses its .fai index when one is present.

# source_knowledge_outline

- Genomic Coordinates
- When to use
- The rule
- The two conversions
- Which format is which
- Variants are not intervals
- Check the assembly before trusting a join
- Audit a file against its own format
- Transcript, CDS, and protein positions
- Reporting results

# knowledge_assets

- `references/format-conventions.md`: Format Conventions
- `references/reference-builds.md`: Reference Builds
- `references/transcript-coordinates.md`: Transcript Coordinates
- `references/variant-representation.md`: Variant Representation

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=4, scripts=5, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/genomic-coordinates`.
