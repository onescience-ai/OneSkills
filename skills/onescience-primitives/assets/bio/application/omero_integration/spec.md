# architecture_overview

OMERO integration primitive for microscopy inventory, metadata export, annotations, ROIs, rendering, and reviewed write workflows against OMERO.server and OMERO.web APIs.

This primitive is distilled from the source Agent Skill `omero-integration`. It is a planning and retrieval primitive. Preserved source payloads, if present, are inert copies for review and later binding; they are not executable runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

>-

# source_knowledge_outline

- OMERO Integration
- Verified Baseline
- Operating Contract
- Choose the Interface
- Install a Reproducible Client
- Download the matching 3.6.5 wheel from the official OMERO-linked matrix.
- Credentials and Connection
- Supply OMERO_PASSWORD through the environment/secret manager, or use
- OMERO_SESSION_KEY as an alternative. Do not echo either value.
- Bundled Safe Helpers

# knowledge_assets

- `references/advanced.md`: Advanced
- `references/connection.md`: Connection
- `references/data_access.md`: Data Access
- `references/image_processing.md`: Image Processing
- `references/metadata.md`: Metadata
- `references/rois.md`: Rois
- `references/scripts.md`: Scripts
- `references/sources.md`: Sources
- `references/tables.md`: Tables

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# source_payloads

- `source_payload/scripts/export_image_metadata.py` (source_script): Export Image Metadata
- `source_payload/scripts/inventory.py` (source_script): Inventory
- `source_payload/scripts/omero_common.py` (source_script): Omero Common
- `source_payload/scripts/plan_transfer.py` (source_script): Plan Transfer
- `source_payload/scripts/validate_config.py` (source_script): Validate Config

Source payloads are indexed in `metadata.json.source_payloads` with SHA-256 values. They preserve source scripts, templates, and static files for later migration review, but they do not grant execution permission.

# execution_policy

No source scripts were promoted as execution assets in this batch. Source-side file counts were: references=9, scripts=5, assets=0. Preserved source payloads remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/omero-integration`.
