# architecture_overview

Clinical decision-support research primitive for evaluation artifacts, evidence profiles, cohort and biomarker documentation, privacy review, and governance planning.

This primitive is distilled from the source Agent Skill `clinical-decision-support`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Python 3.11+; local files only; bundled scripts use the standard library and require no network, credentials, API keys, LLMs, or image services.

# source_knowledge_outline

- Clinical Decision-Support Research and Evaluation
- Hard Safety Boundary
- In Scope
- Data Gate
- Required Artifact Header
- Workflow
- 1. Frame the Research Question
- 2. Select the Artifact
- 3. Run Locally
- 4. Human Review

# knowledge_assets

- `references/cohort_evaluation.md`: Cohort Evaluation
- `references/decision_logic_traceability.md`: Decision Logic Traceability
- `references/evidence_profiles.md`: Evidence Profiles
- `references/model_biomarker_evaluation.md`: Model Biomarker Evaluation
- `references/privacy_and_disclosure.md`: Privacy And Disclosure
- `references/README.md`: Readme
- `references/regulatory_and_governance.md`: Regulatory And Governance
- `references/safety_and_scope.md`: Safety And Scope
- `references/security_validation.md`: Security Validation
- `references/sources.md`: Sources
- `references/study_reporting.md`: Study Reporting
- `references/survival_analysis.md`: Survival Analysis

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=12, scripts=8, assets=7. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/clinical-decision-support`.
