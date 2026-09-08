# architecture_overview

ISO standards readiness primitive for organizing declared scope, controlled documents, traceability, CAPA, laboratory competence, evidence manifests, and review boundaries.

This primitive is distilled from the source Agent Skill `iso-standards-readiness`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Python 3.11+; bundled CLIs use only the standard library and bounded local JSON/Markdown files, with no network access or credentials.

# source_knowledge_outline

- ISO Standards Readiness Evidence Preparation
- Purpose
- Non-negotiable boundary
- ISO and IEC copyright
- Standards covered
- Current baseline (read the ledger before any time-sensitive statement)
- Keep the assurance lanes separate
- Core workflow
- Step 1: Declare the standard, purpose, and authorized owners
- Step 2: Freeze source/version evidence

# knowledge_assets

- `references/assurance-lanes.md`: Assurance Lanes
- `references/evidence-architecture.md`: Evidence Architecture
- `references/gap-analysis-checklist.md`: Gap Analysis Checklist
- `references/iso-13485.md`: Iso 13485
- `references/iso-14971.md`: Iso 14971
- `references/iso-15189.md`: Iso 15189
- `references/iso-17025.md`: Iso 17025
- `references/quality-manual-guide.md`: Quality Manual Guide
- `references/source-ledger.md`: Source Ledger

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=9, scripts=10, assets=12. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/iso-standards-readiness`.
