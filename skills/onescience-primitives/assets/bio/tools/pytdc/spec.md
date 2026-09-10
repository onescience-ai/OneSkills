# architecture_overview

PyTDC primitive for therapeutic data commons registry discovery, benchmark access, approved dataset splits, evaluator metrics, and bounded molecular-oracle workflows.

This primitive is distilled from the source Agent Skill `pytdc`. It is a planning and retrieval primitive. Preserved source payloads, if present, are inert copies for review and later binding; they are not executable runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires uv, CPython 3.11, PyTDC 1.1.15, and setuptools 80.9.0 for its legacy pkg_resources runtime import. Dataset, benchmark, checkpoint, and remote-oracle operations require network/storage review and explicit user approval.

# source_knowledge_outline

- PyTDC (Therapeutics Data Commons)
- Verified snapshot
- Installation
- Non-negotiable data and network policy
- Cache and cost behavior
- Start with metadata-only discovery
- Dataset workflow
- split keys are: train, valid, test
- Split selection without overclaiming leakage control
- Evaluators

# knowledge_assets

- `references/datasets.md`: Datasets
- `references/oracles.md`: Oracles
- `references/sources.md`: Sources
- `references/utilities.md`: Utilities

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# source_payloads

- `source_payload/scripts/_common.py` (source_script):  Common
- `source_payload/scripts/benchmark_evaluation.py` (source_script): Benchmark Evaluation
- `source_payload/scripts/cache_audit.py` (source_script): Cache Audit
- `source_payload/scripts/discover_metadata.py` (source_script): Discover Metadata
- `source_payload/scripts/load_and_split_data.py` (source_script): Load And Split Data
- `source_payload/scripts/molecular_generation.py` (source_script): Molecular Generation

Source payloads are indexed in `metadata.json.source_payloads` with SHA-256 values. They preserve source scripts, templates, and static files for later migration review, but they do not grant execution permission.

# execution_policy

No source scripts were promoted as execution assets in this batch. Source-side file counts were: references=4, scripts=6, assets=0. Preserved source payloads remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/pytdc`.
