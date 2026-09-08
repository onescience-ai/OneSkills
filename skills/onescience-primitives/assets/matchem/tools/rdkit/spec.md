# architecture_overview

RDKit cheminformatics primitive for molecules, reactions, descriptors, fingerprints, conformers, and structure-based chemistry workflows.

This primitive is distilled from the source Agent Skill `rdkit`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Examples target RDKit 2026.03.x. Use conda-forge for the broadest binary support or PyPI package `rdkit` for supported platform wheels; `rdkit-pypi` is the legacy PyPI name.

# source_knowledge_outline

- RDKit Cheminformatics Toolkit
- Overview
- Installation and Setup
- Core Capabilities
- Common Pitfalls
- Resources
- references/
- scripts/

# knowledge_assets

- `references/api_reference.md`: Api Reference
- `references/core_capabilities.md`: Core Capabilities
- `references/descriptors_reference.md`: Descriptors Reference
- `references/smarts_patterns.md`: Smarts Patterns
- `references/workflows_and_best_practices.md`: Workflows And Best Practices

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=5, scripts=3, assets=0. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/rdkit`.
