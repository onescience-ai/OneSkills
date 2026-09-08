# architecture_overview

Scientific slides primitive for research talk structure, slide design, data visualization, Beamer and PowerPoint assets, visual review, image generation boundaries, and export workflows.

This primitive is distilled from the source Agent Skill `scientific-slides`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

See the migrated references and the source skill for package-specific dependencies. Install dependencies only in the execution environment that needs them.

# source_knowledge_outline

- Scientific Slides
- Overview
- When to Use This Skill
- Slide Generation with Nano Banana Pro
- Default Workflow: PDF Slides (Recommended)
- Presentation Plan: Introduction to Machine Learning
- Slide 1: Title Slide
- Slide 2: Introduction
- Slide 3: Core Concepts
- Title slide (first slide - establishes the style)

# knowledge_assets

- `references/beamer_guide.md`: Beamer Guide
- `references/common_pitfalls.md`: Common Pitfalls
- `references/data_visualization_slides.md`: Data Visualization Slides
- `references/presentation_structure.md`: Presentation Structure
- `references/presentation_workflow.md`: Presentation Workflow
- `references/prompt_writing.md`: Prompt Writing
- `references/script_reference.md`: Script Reference
- `references/slide_capabilities.md`: Slide Capabilities
- `references/slide_design_principles.md`: Slide Design Principles
- `references/talk_types_guide.md`: Talk Types Guide
- `references/visual_review_workflow.md`: Visual Review Workflow

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=11, scripts=7, assets=5. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/scientific-slides`.
