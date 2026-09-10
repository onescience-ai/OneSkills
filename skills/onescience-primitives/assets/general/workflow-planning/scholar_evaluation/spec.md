# architecture_overview

Scholar-evaluation primitive for qualitative-first, evidence-traceable developmental review of scholarly works and low-stakes research-assessment rubrics with optional local quality controls.

This primitive is distilled from the source Agent Skill `scholar-evaluation`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.11+ for optional bundled standard-library CLIs. All tooling is local JSON/CSV processing with no network, credentials, external models, or subprocesses.

# source_knowledge_outline

- Scholar Evaluation
- Purpose
- Hard safety boundary
- ScholarEval status
- Metric and prestige policy
- Data boundary
- Workflow
- 1. Confirm allowed use and authorization
- 2. Define the construct before criteria
- 3. Adapt and validate the rubric

# knowledge_assets

- `references/evaluation_framework.md`: Evaluation Framework
- `references/local_tooling.md`: Local Tooling
- `references/responsible_assessment.md`: Responsible Assessment
- `references/security_validation.md`: Security Validation
- `references/source_ledger.md`: Source Ledger

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=5, scripts=8, assets=5. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/scholar-evaluation`.
