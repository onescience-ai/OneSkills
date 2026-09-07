# architecture_overview

Literature review is a research-synthesis planning primitive. It structures searches, screening, extraction, appraisal, citation verification, and final assembly.

# input_schema

Typical inputs are a review question, domain, date range, databases, inclusion and exclusion criteria, screening strategy, extraction schema, citation style, and final output format.

# output_schema

Expected outputs include search plan, query log, screening counts, extraction table schema, synthesis outline, citation verification plan, and document-generation handoff.

# key_dependencies

- academic search or database tools
- citation manager or DOI verification tool
- markdown, PDF, docx, or slide output primitives
- optional visualization primitive for PRISMA or concept diagrams

# common_modification_points

- systematic vs scoping vs narrative review
- database set and search query syntax
- inclusion and exclusion criteria
- screening and dual-review policy
- extraction fields and quality appraisal method
- citation style and final document format

# implementation_risks

- A review is not systematic if search strings, dates, and counts are missing.
- Single-database searches are usually incomplete.
- Citation errors propagate quickly unless verified.
- Visual requirements should be handed to visualization primitives rather than embedded here.

# provenance

Distilled from `scientific-agent-skills/skills/literature-review` version `1.7`. Scripts, templates, and external search tooling were not copied.
