# typical_workflow

1. Match the task to `matchem.tools.pymatgen` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- pymatgen==2026.5.4 is the latest stable wrapper release (2026-05-04).
- pymatgen-core==2026.7.16 is the latest stable core release (2026-07-16).
- mp-api==0.46.4 is the latest stable Materials Project client
- The current API site is built from 2026.7.16 core documentation. Pinning both
- Pymatgen uses date-based versions. PyPI renders the date with dots; do not
- scripts/composition_structure_validator.py — strict composition/structure

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.
