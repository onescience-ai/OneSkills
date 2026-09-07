# architecture_overview

Scientific writing is a claim-and-evidence workflow primitive for manuscripts, reports, and submission packages. It preserves a separation between drafting, verification, and accountable human approval.

# input_schema

Typical inputs are document type, study design, target venue, reporting guideline, verified sources, claim registry, methods, results, figures, tables, declarations, and confidentiality classification.

# output_schema

Expected outputs include an evidence-bound draft, unresolved-issues list, consistency audit, reporting-coverage record, citation validation report, and human-approval handoff.

# key_dependencies

- citation_management
- literature_review
- scientific_visualization
- Markdown, DOCX, PDF, or other output-format primitive
- local consistency and manifest validation tools

# common_modification_points

- IMRAD or venue-specific structure
- claim and evidence registry
- reporting guideline
- authorship and CRediT metadata
- disclosure, ethics, funding, and data/code statements
- figure and table provenance

# implementation_risks

- Never invent results, methods, citations, approvals, or author information.
- Search snippets and generated summaries do not verify claims.
- Confidential or unpublished material must not be sent to external services without authorization.
- Human authors retain scientific and submission accountability.

# provenance

Distilled from `scientific-agent-skills/skills/scientific-writing` version `2.0`. Scripts, templates, and reference files were not copied.
