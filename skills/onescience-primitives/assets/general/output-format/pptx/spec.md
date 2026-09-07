# architecture_overview

PPTX is a packaged OOXML presentation format. The primitive describes slide structure, template editing, chart and media boundaries, and rendered-output review.

# input_schema

Typical inputs are slide outline, audience, aspect ratio, template path, chart data, figures, speaker notes, and output constraints.

# output_schema

Expected outputs include a `.pptx` or `.potx`, rendered slide previews, validation report, and source-data/figure provenance.

# key_dependencies

- pptx generation library or OOXML editing tools
- LibreOffice for rendering
- optional MarkItDown for text extraction
- optional Poppler or image tools for previews

# common_modification_points

- slide size and template layout
- text boxes and overflow margins
- native PowerPoint charts
- images, icons, and notes
- slide ordering and relationships

# implementation_risks

- Broken OOXML relationships can make a deck unreadable.
- Text overflow and chart corruption may only appear after rendering.
- Template slots and placeholder assets must be removed or replaced coherently.
- A presentation is not a scientific validation of its claims.

# provenance

Distilled from `scientific-agent-skills/skills/pptx` version `2.1`. Scripts and templates were not copied.
