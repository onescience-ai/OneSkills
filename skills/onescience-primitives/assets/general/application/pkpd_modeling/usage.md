# typical_workflow

1. Match the task to `general.application.pkpd_modeling` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- Pharmpy 2.1.1 (2026-05-19) is the practical Python entry point — model-agnostic, drives
- NONMEM 7.6 (user guides dated November 2025) remains the regulatory default. New since 7.5:
- nlmixr2 (requires rxode2 ≥ 5.0.0) is the credible open-source NLME alternative;
- PKPy (PeerJ, 2025) is a Python popPK framework but is GitHub-only — not on PyPI, so
- Open Systems Pharmacology Suite v12 (PK-Sim/MoBi) is the open-source PBPK platform; Simcyp
- references/nca-conventions.md — parameter definitions, lambda_z rules, BLQ handling, steady state

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.
