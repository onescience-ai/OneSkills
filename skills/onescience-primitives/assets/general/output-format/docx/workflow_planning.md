# when_to_use

Use this primitive when a formal report, manuscript, memo, template, or Word-compatible deliverable is requested.

# when_not_to_use

- Use Markdown/Mermaid when editable text is the primary source of truth.
- Use PDF when fixed-layout distribution is the main requirement.
- Use PPTX when the deliverable is a slide deck.

# planning_steps

1. Confirm create vs edit and template constraints.
2. Define page size, headings, tables, figures, and revision semantics.
3. Generate or patch the OOXML package.
4. Render and inspect every page.
5. Validate structure and record provenance.

# fallback

- If the source document is legacy `.doc`, convert before editing.
- If tracked changes or comments are required, use an OOXML-aware path.
- If visual fidelity is uncertain, provide a rendered PDF preview for review.

# handoff_notes

Include source/template path, page settings, content outline, figure/table inputs, revision requirements, and validation outputs.
