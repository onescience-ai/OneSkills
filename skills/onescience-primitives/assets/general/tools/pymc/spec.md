# architecture_overview

PyMC primitive for Bayesian modeling, hierarchical models, MCMC, variational inference, model comparison, posterior checks, and probabilistic programming workflows.

This primitive is distilled from the source Agent Skill `pymc`. It is a planning and retrieval primitive. Preserved source payloads, if present, are inert copies for review and later binding; they are not executable runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.12+ and PyMC 6.0.1-compatible dependencies. Install reproducible environments with `uv pip install "pymc[nutpie]==6.0.1"`; optional NumPyro or BlackJAX samplers require separately pinned JAX-compatible dependencies.

# source_knowledge_outline

- PyMC Bayesian Modeling
- Overview
- Current Version and Setup
- When to Use This Skill
- Standard Bayesian Workflow
- Distribution Selection Guide
- For Priors
- For Likelihoods
- Sampling and Inference
- MCMC with NUTS

# knowledge_assets

- `references/distributions.md`: Distributions
- `references/model_patterns.md`: Model Patterns
- `references/sampling_inference.md`: Sampling Inference
- `references/standard_workflow.md`: Standard Workflow
- `references/workflows.md`: Workflows

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# source_payloads

- `source_payload/scripts/model_comparison.py` (source_script): Model Comparison
- `source_payload/scripts/model_diagnostics.py` (source_script): Model Diagnostics
- `source_payload/assets/hierarchical_model_template.py` (source_asset): Hierarchical Model Template
- `source_payload/assets/linear_regression_template.py` (source_asset): Linear Regression Template

Source payloads are indexed in `metadata.json.source_payloads` with SHA-256 values. They preserve source scripts, templates, and static files for later migration review, but they do not grant execution permission.

# execution_policy

No source scripts were promoted as execution assets in this batch. Source-side file counts were: references=5, scripts=2, assets=2. Preserved source payloads remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/pymc`.
