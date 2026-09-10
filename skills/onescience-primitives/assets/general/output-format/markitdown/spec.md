# architecture_overview

MarkItDown output-format primitive for trusted local document-to-Markdown conversion, stream conversion, plugin workflows, OCR extraction, and batch ingestion.

This primitive is distilled from the source Agent Skill `markitdown`. It is a planning and retrieval primitive. Preserved source payloads, if present, are inert copies for review and later binding; they are not executable runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Python 3.10+ and uv. Examples target MarkItDown 0.1.6. Core local conversion can run offline; URL, YouTube, audio transcription, LLM, Azure, and MCP workflows may use network or external services.

# source_knowledge_outline

- MarkItDown
- Overview
- Choose the Right Path
- Installation
- Quick Start
- Command line
- Convert a trusted local file
- Write Markdown to stdout
- Supply type information when reading bytes from stdin
- Python: trusted local file

# knowledge_assets

- `references/api_reference.md`: Api Reference
- `references/cloud_and_ocr.md`: Cloud And Ocr
- `references/file_formats.md`: File Formats
- `references/mcp_and_plugins.md`: Mcp And Plugins
- `references/migration.md`: Migration
- `references/security.md`: Security
- `references/workflows.md`: Workflows

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# source_payloads

- `source_payload/scripts/batch_convert.py` (source_script): Batch Convert
- `source_payload/scripts/convert_literature.py` (source_script): Convert Literature
- `source_payload/scripts/inspect_installation.py` (source_script): Inspect Installation

Source payloads are indexed in `metadata.json.source_payloads` with SHA-256 values. They preserve source scripts, templates, and static files for later migration review, but they do not grant execution permission.

# execution_policy

No source scripts were promoted as execution assets in this batch. Source-side file counts were: references=7, scripts=3, assets=0. Preserved source payloads remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/markitdown`.
