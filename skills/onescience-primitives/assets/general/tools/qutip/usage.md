# typical_workflow

1. Match the task to `general.tools.qutip` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- qutip-qip 0.4.2 (2026-06-23) is the production/stable circuit, gate, and
- qutip-qtrl 0.2.0 (2026-06-23) provides GRAPE and CRAB **quantum optimal
- qutip-jax 0.1.1 (2025-05-29) is the official JAX data backend for GPU and
- qutip-cupy is an official QuTiP-organization repository, but it has no PyPI
- Import HEOM from qutip.solver.heom; the legacy QuTiP 4 nonmarkov HEOM
- Use FloquetBasis for modes and quasi-energies. Verify

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.
