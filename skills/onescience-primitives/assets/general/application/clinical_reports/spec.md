# architecture_overview

Clinical reporting primitive for draft report structures, aggregate tables, review manifests, provenance preservation, and deterministic structural checks on verified authorized facts.

This primitive is distilled from the source Agent Skill `clinical-reports`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Requires Python 3.11+ only for optional dependency-free local scripts; no network access, credentials, external models, or image services.

# source_knowledge_outline

- Clinical Reports
- Purpose
- Non-Negotiable Boundary
- Input Gate
- Route Before Drafting
- Safe Drafting Workflow
- 1. Create a source-fact manifest
- 2. Generate the correct template
- 3. Populate verified fields only
- 4. Run deterministic checks

# knowledge_assets

- `references/case_report_guidelines.md`: Case Report Guidelines
- `references/clinical_trial_reporting.md`: Clinical Trial Reporting
- `references/data_presentation.md`: Data Presentation
- `references/diagnostic_reports_standards.md`: Diagnostic Reports Standards
- `references/medical_terminology.md`: Medical Terminology
- `references/privacy_and_deidentification.md`: Privacy And Deidentification
- `references/professional_review.md`: Professional Review
- `references/README.md`: Readme
- `references/report_type_routing.md`: Report Type Routing
- `references/safety_reporting.md`: Safety Reporting
- `references/sources.md`: Sources

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=11, scripts=9, assets=15. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/clinical-reports`.
