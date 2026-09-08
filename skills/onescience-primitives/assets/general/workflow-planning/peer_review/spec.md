# architecture_overview

Peer-review primitive for evidence-bounded manuscript assessment, claim-evidence checks, reporting-guideline selection, methods critique, reproducibility review, and revision-response planning.

This primitive is distilled from the source Agent Skill `peer-review`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Python 3.11+ standard library. Bundled CLIs are deterministic and local-only; they accept bounded JSON, CSV, or Markdown and make no network, model, image, or external-service calls.

# source_knowledge_outline

- Peer Review
- Mandatory safety boundary
- Human accountability
- Intake gate
- Review workflow
- 1. Establish scope and available evidence
- 2. Orient without deciding
- 3. Select reporting guidance
- 4. Map claims to evidence
- 5. Review methods and statistics

# knowledge_assets

- `references/common_issues.md`: Common Issues
- `references/ethical_review_practice.md`: Ethical Review Practice
- `references/reporting_standards.md`: Reporting Standards
- `references/security_validation.md`: Security Validation
- `references/statistical_reproducibility.md`: Statistical Reproducibility
- `references/tool_reference.md`: Tool Reference

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=6, scripts=8, assets=9. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/peer-review`.
