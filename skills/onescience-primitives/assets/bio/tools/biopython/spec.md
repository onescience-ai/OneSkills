# architecture_overview

Biopython primitive for biological sequences, records, annotations, file formats, Entrez-style retrieval planning, and phylogenetic utilities.

This primitive is distilled from the source Agent Skill `biopython`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.10+, NumPy, and Biopython. Entrez and web BLAST examples require network access; local BLAST/MUSCLE examples require those command-line tools installed separately.

# source_knowledge_outline

- Biopython: Computational Molecular Biology in Python
- Overview
- When to Use This Skill
- Core Capabilities
- Installation and Setup
- Optional: register at https://www.ncbi.nlm.nih.gov/account/settings/
- Using This Skill
- 1. Sequence Handling (Bio.Seq & Bio.SeqIO)
- Read sequences from FASTA file
- Convert GenBank to FASTA

# knowledge_assets

- `references/advanced.md`: Advanced
- `references/alignment.md`: Alignment
- `references/blast.md`: Blast
- `references/databases.md`: Databases
- `references/phylogenetics.md`: Phylogenetics
- `references/sequence_io.md`: Sequence Io
- `references/structure.md`: Structure

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=7, scripts=0, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/biopython`.
