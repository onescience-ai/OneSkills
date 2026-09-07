# architecture_overview

DOCX is a packaged OOXML document format. The primitive describes document structure, safe creation/editing paths, and verification requirements.

# input_schema

Typical inputs are document content, template path, page size, heading hierarchy, tables, images, comments or tracked changes, and target audience.

# output_schema

Expected outputs include a `.docx` or `.dotx`, rendered preview, validation report, and source-data or image provenance notes.

# key_dependencies

- docx generation library or OOXML editing tools
- LibreOffice for rendering
- optional pandoc for extraction
- optional Poppler for PDF/image previews

# common_modification_points

- page size and orientation
- heading styles and table widths
- list numbering
- image placement and dimensions
- tracked changes and comments
- template-derived content

# implementation_risks

- A DOCX is a ZIP/XML package, so careless reserialization can corrupt it.
- Rendered appearance must be checked, especially tables, images, and page breaks.
- A polished template does not prove scientific completeness or submission compliance.

# provenance

Distilled from `scientific-agent-skills/skills/docx` version `2.1`. Editing scripts and templates were not copied.
