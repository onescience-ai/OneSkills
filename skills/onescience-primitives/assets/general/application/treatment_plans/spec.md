# architecture_overview

Treatment-plan primitive for research-only plan structures, source-fact manifests, consistency checks, and review-ready documentation assembly.

This primitive is distilled from the source Agent Skill `treatment-plans`. It is a planning and retrieval primitive, not a direct copy of the source skill runtime.

# input_schema

Typical inputs include the user research goal, available data or artifacts, target package or platform version, execution environment constraints, and desired output type.

# output_schema

Expected outputs include source-grounded workflow guidance, relevant parameters or APIs, validation checks, caveats, and downstream executor handoff notes.

# key_dependencies

Python 3.11+ standard library; local JSON files only. Bundled CLIs require no network, external services, models, images, credentials, environment variables, or third-party packages.

# source_knowledge_outline

- Treatment-Plan Documentation
- Hard safety boundary
- Required visible notice
- Data gate
- Allowed inputs
- Workflow
- 1. Establish authority and intended use
- 2. Generate a generic package
- 3. Transcribe supplied decisions without inference
- 4. Run deterministic local checks

# knowledge_assets

- `references/documentation_workflow.md`: Documentation Workflow
- `references/privacy_governance.md`: Privacy Governance
- `references/README.md`: Readme
- `references/safety_scope.md`: Safety Scope
- `references/security_validation.md`: Security Validation
- `references/shared_decision_handoff.md`: Shared Decision Handoff
- `references/source_boundaries.md`: Source Boundaries
- `references/source_ledger.md`: Source Ledger

All listed references are read-only knowledge assets indexed in `metadata.json` with SHA-256 values.

# execution_policy

No source scripts were promoted in this batch. Source-side file counts were: references=8, scripts=8, assets=6. Scripts and non-reference assets remain migration candidates until an explicit input/output contract, dependency policy, side-effect boundary, and execution-asset allowlist are added.

# implementation_risks

- Do not treat source documentation snapshots as live upstream guarantees.
- Do not run copied or source-side scripts unless a primitive declares them in `# execution_assets`.
- Validate scientific assumptions, units, identifiers, versions, and provenance before interpreting results.

# provenance

Distilled from `scientific-agent-skills/skills/treatment-plans`.
