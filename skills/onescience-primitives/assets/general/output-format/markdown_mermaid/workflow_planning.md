# when_to_use

Use this primitive when a scientific document, README, workflow diagram, architecture note, or version-controlled report is required.

# when_not_to_use

- Use scientific_visualization for numeric data plots.
- Use docx, pdf, or pptx output primitives when the requested deliverable is a fixed office or print format.
- Use a specialized schematic primitive when the figure requires non-text rendering.

# planning_steps

1. Identify document type and target renderer.
2. Draft the text source and outline.
3. Select the correct Mermaid diagram type.
4. Add citations and accessibility metadata.
5. Preview and optionally derive binary formats.

# fallback

- If Mermaid is unsupported, keep the source and provide a plain-text fallback.
- If a diagram is too data-rich for Mermaid, hand off to scientific_visualization.

# handoff_notes

Include document type, audience, renderer, diagram relationships, citation style, and derivative format requirements.
