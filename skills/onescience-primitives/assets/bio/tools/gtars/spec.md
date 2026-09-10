# architecture_overview

Gtars primitive for genomic interval models, set algebra, overlaps and counts, consensus and coverage, tokenization, fragment processing, and refget/BEDbase planning.

This primitive is distilled from the source Agent Skill `gtars`. It is a planning and retrieval primitive. Preserved source payloads, if present, are inert copies for review and later binding; they are not executable runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Python bindings require Python 3.10+ and gtars 0.9.2. The Rust meta-crate and gtars-cli are 0.9.0 and require a Rust toolchain supporting Edition 2024; upstream declares no rust-version. Bundled audit CLIs use only Python 3.10+ standard library and are local/network-free. Remote constructors, pretrained tokenizers, refget, and BEDbase caching require explicit network and storage approval.

# source_knowledge_outline

- Gtars
- Verified snapshot (2026-07-23)
- Native-code trust gate and exact pins
- Genomic data contract
- Safe local workflow
- Current Python core
- rows: [{"chr": ..., "start": ..., "end": ..., "count": ...}, ...]
- Tokenizers, fragments, and reference stores
- Network and cache gate
- Sensitive metadata and leakage

# knowledge_assets

- `references/cli.md`: Cli
- `references/coverage.md`: Coverage
- `references/overlap.md`: Overlap
- `references/python-api.md`: Python Api
- `references/refget.md`: Refget
- `references/tokenizers.md`: Tokenizers

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# source_payloads

- `source_payload/scripts/__init__.py` (source_script):   Init  
- `source_payload/scripts/_common.py` (source_script):  Common
- `source_payload/scripts/artifact_inspector.py` (source_script): Artifact Inspector
- `source_payload/scripts/bed_validator.py` (source_script): Bed Validator
- `source_payload/scripts/coverage_preflight.py` (source_script): Coverage Preflight
- `source_payload/scripts/execution_plan.py` (source_script): Execution Plan
- `source_payload/scripts/refget_digest_plan.py` (source_script): Refget Digest Plan
- `source_payload/scripts/tokenizer_manifest.py` (source_script): Tokenizer Manifest

Source payloads are indexed in `metadata.json.source_payloads` with SHA-256 values. They preserve source scripts, templates, and static files for later migration review, but they do not grant execution permission.

# execution_policy

No source scripts were promoted as execution assets in this batch. Source-side file counts were: references=6, scripts=8, assets=0. Preserved source payloads remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/gtars`.
