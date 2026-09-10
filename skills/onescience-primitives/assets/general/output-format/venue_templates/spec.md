# architecture_overview

Venue-templates primitive for journal manuscripts, conference papers, research posters, and grant documents using venue-specific formatting guidance and bundled LaTeX scaffolds.

This primitive is distilled from the source Agent Skill `venue-templates`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.11+ for helper scripts; LaTeX and Poppler command-line tools are optional for compilation and PDF inspection.

# source_knowledge_outline

- Venue Templates
- Mandatory Currency Rule
- When to Use
- Verification-First Workflow
- 1. Resolve the exact target
- 2. Consult the right reference
- 3. Capture a compliance note
- 4. Start from the official template
- 5. Validate manually and mechanically
- Bundled Assets

# knowledge_assets

- `references/cell_press_style.md`: Cell Press Style
- `references/conferences_formatting.md`: Conferences Formatting
- `references/cs_conference_style.md`: Cs Conference Style
- `references/grants_requirements.md`: Grants Requirements
- `references/journals_formatting.md`: Journals Formatting
- `references/medical_journal_styles.md`: Medical Journal Styles
- `references/ml_conference_style.md`: Ml Conference Style
- `references/nature_science_style.md`: Nature Science Style
- `references/posters_guidelines.md`: Posters Guidelines
- `references/reviewer_expectations.md`: Reviewer Expectations
- `references/venue_writing_styles.md`: Venue Writing Styles

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=11, scripts=3, assets=16. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/venue-templates`.
