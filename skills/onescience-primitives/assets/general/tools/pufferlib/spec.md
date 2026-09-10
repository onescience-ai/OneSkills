# architecture_overview

PufferLib primitive for reinforcement-learning environments, vectorization, policy training, evaluation planning, and safe checkpoint review across published source lines.

This primitive is distilled from the source Agent Skill `pufferlib`. It is a planning and retrieval primitive. Preserved source payloads, if present, are inert copies for review and later binding; they are not executable runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Bundled CLIs require Python 3.10+ and use only the standard library. Published pufferlib 3.0.0 supports Python >=3.9 but ships as a native-code source archive; current 4.0 source requires Python >=3.10, Torch >=2.9, and an audited CPU/CUDA toolchain. Network, GPU, native builds, environment plug-ins, assets, checkpoints, and external logging are never required by the bundled CLIs.

# source_knowledge_outline

- PufferLib
- Safe defaults
- First local checks
- Installation and provenance
- Published 3.0.0
- Current 4.0 source
- Environment workflow
- 1. Validate the contract
- 2. Adapt only after review
- 3. Native environments

# knowledge_assets

- `references/environments.md`: Environments
- `references/integration.md`: Integration
- `references/policies.md`: Policies
- `references/training.md`: Training
- `references/vectorization.md`: Vectorization

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# source_payloads

- `source_payload/scripts/__init__.py` (source_script):   Init  
- `source_payload/scripts/_common.py` (source_script):  Common
- `source_payload/scripts/benchmark_vectorization.py` (source_script): Benchmark Vectorization
- `source_payload/scripts/env_contract_validator.py` (source_script): Env Contract Validator
- `source_payload/scripts/env_template.py` (source_script): Env Template
- `source_payload/scripts/inspect_checkpoint.py` (source_script): Inspect Checkpoint
- `source_payload/scripts/repro_plan.py` (source_script): Repro Plan
- `source_payload/scripts/train_template.py` (source_script): Train Template
- `source_payload/scripts/validate_plan.py` (source_script): Validate Plan

Source payloads are indexed in `metadata.json.source_payloads` with SHA-256 values. They preserve source scripts, templates, and static files for later migration review, but they do not grant execution permission.

# execution_policy

No source scripts were promoted as execution assets in this batch. Source-side file counts were: references=5, scripts=9, assets=0. Preserved source payloads remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/pufferlib`.
