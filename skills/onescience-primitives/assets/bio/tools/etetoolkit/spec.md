# architecture_overview

ETE toolkit primitive for tree I/O, topology manipulation, subtree comparison, taxonomy workflows, SmartView exploration, and tree rendering.

This primitive is distilled from the source Agent Skill `etetoolkit`. It is a planning and retrieval primitive. Preserved source payloads, if present, are inert copies for review and later binding; they are not executable runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Bundled scripts require Python 3.10+ and ete4 4.4.0 (upstream ete4 supports Python >=3.7). Taxonomy setup and SmartView exploration need network access; static SmartView PNG rendering needs ete4[render-sm], and Qt PDF/SVG rendering needs ete4[treeview].

# source_knowledge_outline

- ETE Toolkit 4
- Scope
- Current Target
- Installation
- SmartView static PNG screenshots
- Legacy Qt renderer for PNG, PDF, and SVG
- Quick Start
- Use an open file object for files; reserve strings for Newick text.
- Search and annotate.
- Keep selected tips while preserving pairwise branch-length distances.

# knowledge_assets

- `references/api_reference.md`: Api Reference
- `references/migration-ete3-to-ete4.md`: Migration Ete3 To Ete4
- `references/taxonomy.md`: Taxonomy
- `references/visualization.md`: Visualization
- `references/workflows.md`: Workflows

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# source_payloads

- `source_payload/scripts/quick_visualize.py` (source_script): Quick Visualize
- `source_payload/scripts/tree_operations.py` (source_script): Tree Operations

Source payloads are indexed in `metadata.json.source_payloads` with SHA-256 values. They preserve source scripts, templates, and static files for later migration review, but they do not grant execution permission.

# execution_policy

No source scripts were promoted as execution assets in this batch. Source-side file counts were: references=5, scripts=2, assets=0. Preserved source payloads remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/etetoolkit`.
