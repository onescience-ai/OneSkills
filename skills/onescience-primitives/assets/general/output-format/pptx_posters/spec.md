# architecture_overview

PPTX poster primitive for scientific poster planning, manifest-driven layout, PowerPoint generation, palette and layout checks, image inventory, source ledgers, and security validation.

This primitive is distilled from the source Agent Skill `pptx-posters`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.10+, uv, and exact generation pins python-pptx 1.0.2, Pillow 12.3.0, and lxml 6.1.1. Validation and PPTX ZIP/XML inspection are local and network-free; final PowerPoint, accessibility, PDF, printer, and author review are manual.

# source_knowledge_outline

- PPTX posters
- Scope
- Hard gates
- Install exact generation dependencies
- Establish requirements before layout
- Build the manifest
- Audit assets and palette before generation
- Generate the PPTX
- Run final technical audits
- Manual PowerPoint and accessibility gate

# knowledge_assets

- `references/manifest_spec.md`: Manifest Spec
- `references/poster_content_guide.md`: Poster Content Guide
- `references/poster_design_principles.md`: Poster Design Principles
- `references/poster_layout_design.md`: Poster Layout Design
- `references/pptx_security.md`: Pptx Security
- `references/security_validation.md`: Security Validation
- `references/source_ledger.md`: Source Ledger

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=7, scripts=10, assets=3. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/pptx-posters`.
