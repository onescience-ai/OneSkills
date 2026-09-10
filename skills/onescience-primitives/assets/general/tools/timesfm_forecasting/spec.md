# architecture_overview

TimesFM forecasting primitive for zero-shot univariate time-series forecasting, preflight system checks, interval outputs, and batch prediction.

This primitive is distilled from the source Agent Skill `timesfm-forecasting`. It is a planning and retrieval primitive. Preserved source payloads, if present, are inert copies for review and later binding; they are not executable runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

See the migrated references and the source skill for package-specific dependencies. Install dependencies only in the execution environment that needs them.

# source_knowledge_outline

- TimesFM Forecasting
- Overview
- When to Use This Skill
- ⚠️ Mandatory Preflight: System Requirements Check
- Hardware Requirements by Model Version
- 🔧 Installation
- Step 1: Verify System (always first)
- Step 2: Install TimesFM
- Using uv (recommended by this repo)
- For JAX/Flax backend (faster on TPU/GPU)

# knowledge_assets

- `references/api_reference.md`: Api Reference
- `references/data_preparation.md`: Data Preparation
- `references/examples_and_validation.md`: Examples And Validation
- `references/output_and_config.md`: Output And Config
- `references/performance_tuning.md`: Performance Tuning
- `references/system_requirements.md`: System Requirements
- `references/workflows.md`: Workflows

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# source_payloads

- `source_payload/scripts/check_system.py` (source_script): Check System
- `source_payload/scripts/forecast_csv.py` (source_script): Forecast Csv

Source payloads are indexed in `metadata.json.source_payloads` with SHA-256 values. They preserve source scripts, templates, and static files for later migration review, but they do not grant execution permission.

# execution_policy

No source scripts were promoted as execution assets in this batch. Source-side file counts were: references=7, scripts=2, assets=0. Preserved source payloads remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/timesfm-forecasting`.
