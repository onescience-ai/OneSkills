# architecture_overview

LaTeX posters primitive for professional research posters using beamerposter, tikzposter, or baposter, including layout design, color schemes, multi-column formats, figure integration, and poster-specific communication guidance.

This primitive is distilled from the source Agent Skill `latex-posters`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

See the migrated references and the source skill for package-specific dependencies. Install dependencies only in the execution environment that needs them.

# source_knowledge_outline

- LaTeX Research Posters
- Overview
- When to Use This Skill
- AI-Powered Visual Element Generation
- Hard limits (do not exceed)
- Scientific Schematics Integration
- Core Capabilities
- Workflow for Poster Creation
- Stage 1: Planning and Content Development
- Stage 2: Generate Visual Elements (AI-Powered)

# knowledge_assets

- `references/ai_graphics_for_posters.md`: Ai Graphics For Posters
- `references/compilation_and_quality_control.md`: Compilation And Quality Control
- `references/latex_poster_packages.md`: Latex Poster Packages
- `references/latex_poster_reference.md`: Latex Poster Reference
- `references/poster_content_guide.md`: Poster Content Guide
- `references/poster_design_principles.md`: Poster Design Principles
- `references/poster_layout_design.md`: Poster Layout Design
- `references/poster_patterns_and_presentation.md`: Poster Patterns And Presentation
- `references/README.md`: Readme

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=9, scripts=3, assets=4. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/latex-posters`.
