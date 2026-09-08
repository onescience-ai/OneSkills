# typical_workflow

1. Match the task to `cfd.tools.fluidsim` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- Latest stable PyPI release: fluidsim==0.9.0 (2025-12-04).
- Package metadata requires Python >=3.11 and lists Python 3.11–3.14.
- Pseudospectral parameter creation needs FluidFFT; bare fluidsim imported in
- Current companion versions tested here: fluidfft==0.4.5 and
- fluidfft-fftw==0.0.1: sequential
- fluidfft-mpi-with-fftw==0.0.1: MPI

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.
