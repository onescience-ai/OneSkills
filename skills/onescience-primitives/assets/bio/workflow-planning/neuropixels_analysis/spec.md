# architecture_overview

Neuropixels analysis primitive for loading SpikeGLX, Open Ephys, or NWB recordings, preprocessing, motion correction, spike sorting, quality metrics, and unit curation.

This primitive is distilled from the source Agent Skill `neuropixels-analysis`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

See the migrated references and the source skill for package-specific dependencies. Install dependencies only in the execution environment that needs them.

# source_knowledge_outline

- Neuropixels Data Analysis
- Overview
- When to Use This Skill
- Supported Hardware & Formats
- Quick Start
- Import and configure parallel processing
- Global job kwargs are reused by all parallelizable steps
- Loading data
- Inspect available streams first
- SpikeGLX (most common) — select the AP stream by name

# knowledge_assets

- `references/AI_CURATION.md`: Ai Curation
- `references/ANALYSIS.md`: Analysis
- `references/api_reference.md`: Api Reference
- `references/AUTOMATED_CURATION.md`: Automated Curation
- `references/MOTION_CORRECTION.md`: Motion Correction
- `references/plotting_guide.md`: Plotting Guide
- `references/PREPROCESSING.md`: Preprocessing
- `references/QUALITY_METRICS.md`: Quality Metrics
- `references/SPIKE_SORTING.md`: Spike Sorting
- `references/standard_workflow.md`: Standard Workflow

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=10, scripts=6, assets=1. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/neuropixels-analysis`.
