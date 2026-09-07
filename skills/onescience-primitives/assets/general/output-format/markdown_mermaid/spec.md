# architecture_overview

Markdown with embedded Mermaid is the canonical text output for scientific documentation and structural diagrams. Binary images are optional derivatives, not the source of truth.

# input_schema

Typical inputs are document type, content outline, relationships to diagram, audience, citation needs, and target Markdown renderer.

# output_schema

Expected outputs include a Markdown document, embedded Mermaid source, citations or footnotes, and optional rendered image derivatives.

# key_dependencies

- Markdown renderer
- Mermaid-compatible viewer or CLI for preview
- optional document template

# common_modification_points

- document template and heading structure
- diagram type selection
- accessibility title and description
- citation and footnote style
- image derivative policy

# implementation_risks

- Mermaid syntax support varies by renderer.
- Binary diagrams can drift from the Markdown source if generated manually.
- A diagram without an accessible description is incomplete for many delivery contexts.

# provenance

Distilled from `scientific-agent-skills/skills/markdown-mermaid-writing` version `1.1`. Templates and reference files were not copied.
