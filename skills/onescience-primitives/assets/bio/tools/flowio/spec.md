# architecture_overview

FlowIO primitive for FCS metadata inspection, event extraction, file parsing and writing, and preprocessing-aware flow cytometry I/O.

This primitive is distilled from the source Agent Skill `flowio`. It is a planning and retrieval primitive. Preserved source payloads, if present, are inert copies for review and later binding; they are not executable runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.9-3.13, uv, and FlowIO 1.4.0. NumPy is installed with FlowIO; pandas is optional for DataFrame workflows. Runtime parsing is local and needs no credentials or network access.

# source_knowledge_outline

- FlowIO
- Purpose
- Install
- Operating Workflow
- Critical Semantics
- TEXT keys are normalized
- Events have two representations
- Channel numbering uses two conventions
- Writing is intentionally limited
- Quick Start: Read an FCS File

# knowledge_assets

- `references/api_reference.md`: Api Reference
- `references/fcs_semantics.md`: Fcs Semantics
- `references/sources.md`: Sources
- `references/troubleshooting.md`: Troubleshooting
- `references/workflows.md`: Workflows

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# source_payloads

- `source_payload/scripts/inspect_fcs.py` (source_script): Inspect Fcs

Source payloads are indexed in `metadata.json.source_payloads` with SHA-256 values. They preserve source scripts, templates, and static files for later migration review, but they do not grant execution permission.

# execution_policy

No source scripts were promoted as execution assets in this batch. Source-side file counts were: references=5, scripts=1, assets=0. Preserved source payloads remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/flowio`.
