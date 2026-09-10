# architecture_overview

DNAnexus integration primitive for dx CLI and dxpy automation, project and file management, app and workflow execution, and Nextflow import.

This primitive is distilled from the source Agent Skill `dnanexus-integration`. It is a planning and retrieval primitive. Preserved source payloads, if present, are inert copies for review and later binding; they are not executable runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires a DNAnexus account, network access, Python 3.11+, and dx-toolkit/dxpy; some workflow and infrastructure features require organization licenses or policies.

# source_knowledge_outline

- DNAnexus Integration
- Purpose
- Operating Contract
- Install and Authenticate
- Safe Preflight
- Choose the Right Path
- Core Workflows
- Transfer data
- Search accurately with dxpy
- Build an applet

# knowledge_assets

- `references/app-development.md`: App Development
- `references/authentication.md`: Authentication
- `references/configuration.md`: Configuration
- `references/data-operations.md`: Data Operations
- `references/job-execution.md`: Job Execution
- `references/operations-and-troubleshooting.md`: Operations And Troubleshooting
- `references/python-sdk.md`: Python Sdk
- `references/sources.md`: Sources
- `references/workflow-languages.md`: Workflow Languages

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# source_payloads

- `source_payload/scripts/inspect_dxpy.py` (source_script): Inspect Dxpy
- `source_payload/scripts/validate_dxapp.py` (source_script): Validate Dxapp

Source payloads are indexed in `metadata.json.source_payloads` with SHA-256 values. They preserve source scripts, templates, and static files for later migration review, but they do not grant execution permission.

# execution_policy

No source scripts were promoted as execution assets in this batch. Source-side file counts were: references=9, scripts=2, assets=0. Preserved source payloads remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/dnanexus-integration`.
