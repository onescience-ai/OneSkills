# architecture_overview

LatchBio integration primitive for Python workflow authoring, data staging, registry operations, launch metadata, remote registration, and run monitoring.

This primitive is distilled from the source Agent Skill `latchbio-integration`. It is a planning and retrieval primitive. Preserved source payloads, if present, are inert copies for review and later binding; they are not executable runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires network access and a Latch account. The current stable SDK requires Python 3.9+; Python 3.12 is recommended. Uses uv for installation. Docker is needed for local image builds, while remote registration is the CLI default.

# source_knowledge_outline

- LatchBio Integration
- Current Baseline
- When to Use
- Route to the Right Reference
- Installation and Authentication
- Fast Path
- Minimal Python Workflow
- Recommended Development Lifecycle
- Operational Safety
- Inspect the Installed SDK

# knowledge_assets

- `references/data-management.md`: Data Management
- `references/latch-mcp.md`: Latch Mcp
- `references/nextflow-snakemake.md`: Nextflow Snakemake
- `references/operations-and-debugging.md`: Operations And Debugging
- `references/registry.md`: Registry
- `references/resource-configuration.md`: Resource Configuration
- `references/ui-and-automation.md`: Ui And Automation
- `references/verified-workflows.md`: Verified Workflows
- `references/workflow-creation.md`: Workflow Creation

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# source_payloads

- `source_payload/scripts/inspect_latch_sdk.py` (source_script): Inspect Latch Sdk

Source payloads are indexed in `metadata.json.source_payloads` with SHA-256 values. They preserve source scripts, templates, and static files for later migration review, but they do not grant execution permission.

# execution_policy

No source scripts were promoted as execution assets in this batch. Source-side file counts were: references=9, scripts=1, assets=0. Preserved source payloads remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/latchbio-integration`.
