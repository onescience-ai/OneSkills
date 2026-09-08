# typical_workflow

1. Match the task to `matchem.workflow-planning.molecular_dynamics` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- OpenMM (https://openmm.org/): High-performance MD simulation engine with GPU support, Python API, and flexible force field support
- MDAnalysis (https://mdanalysis.org/): Python library for reading, writing, and analyzing MD trajectories from all major simulation packages
- Protein stability analysis: How does a mutation affect protein dynamics?
- Drug binding simulations: Characterize binding mode and residence time of a ligand
- Conformational sampling: Explore protein flexibility and conformational changes
- Protein-protein interaction: Model interface dynamics and binding energetics

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.
