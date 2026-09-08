# architecture_overview

Geniml primitive for genomic language models, BED/region workflows, consensus universes, embeddings, and tokenization planning.

This primitive is distilled from the source Agent Skill `geniml`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.10+ and uv. Guidance targets geniml 0.8.4 with gtars 0.9.2; ML workflows need the pinned ml extra and compatible native wheels. Bundled planners and inspectors are dependency-free, local-only, and make no network requests.

# source_knowledge_outline

- Geniml
- Verified release snapshot
- Install reproducibly
- Start with the safety gate
- Coordinate and assembly contract
- Current API map
- Region and tokenizer I/O
- Region2Vec
- scEmbed
- BEDspace

# knowledge_assets

- `references/bedspace.md`: Bedspace
- `references/consensus_peaks.md`: Consensus Peaks
- `references/region2vec.md`: Region2Vec
- `references/scembed.md`: Scembed
- `references/utilities.md`: Utilities

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=5, scripts=8, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/geniml`.
