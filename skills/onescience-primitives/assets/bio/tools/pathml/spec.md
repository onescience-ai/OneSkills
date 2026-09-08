# architecture_overview

PathML primitive for computational pathology workflows covering whole-slide image loading, preprocessing, tiling, graph construction, quality control, multiparametric data, and machine-learning planning.

This primitive is distilled from the source Agent Skill `pathml`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

PathML 3.0.5 is the latest PyPI release and targets Python 3.10-3.12; installation needs uv plus platform libraries for OpenSlide, BLAS/LAPACK, and Java/Bio-Formats. Bundled Python 3.10+ CLIs are local, bounded, dependency-free, and network-free.

# source_knowledge_outline

- PathML
- Scope and safety boundary
- Version baseline, verified 2026-07-23
- Reproducible installation
- Debian/Ubuntu
- macOS
- Windows OpenSlide option documented upstream
- Stable minimal workflow
- Research workflow
- No-network default and explicit consent gate

# knowledge_assets

- `references/data_management.md`: Data Management
- `references/graphs.md`: Graphs
- `references/image_loading.md`: Image Loading
- `references/machine_learning.md`: Machine Learning
- `references/multiparametric.md`: Multiparametric
- `references/preprocessing.md`: Preprocessing

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=6, scripts=6, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/pathml`.
