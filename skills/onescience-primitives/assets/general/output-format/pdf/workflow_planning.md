# when_to_use

Use this primitive when a fixed-layout report, archival file, extracted table, merged document, or scanned-document OCR result is required.

# when_not_to_use

- Use DOCX for editable Word deliverables.
- Use PPTX for presentation decks.
- Use Markdown/Mermaid for source-controlled editable documentation.

# planning_steps

1. Determine the PDF operation and fidelity requirement.
2. Choose extraction, generation, or page-operation tooling.
3. Preserve source metadata and provenance.
4. Render or inspect the final pages.
5. Validate page order, content, and security state.

# fallback

- If extraction loses structure, use a layout-aware parser or render pages to images.
- If OCR is uncertain, mark text as machine-extracted and retain page images.
- If the file is password-protected, request authorized access rather than bypassing controls.

# handoff_notes

Include source file, target operation, page range, output settings, OCR/security requirements, and inspection criteria.
