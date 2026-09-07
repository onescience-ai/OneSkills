# typical_workflow

1. Match the task to `general.application.clinical_decision_support` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- diagnose or classify a person;
- recommend, select, sequence, start, stop, or modify treatment;
- calculate or communicate a patient-specific dose;
- triage, prioritize, alarm, alert, or determine urgency;
- make or automate a patient-specific clinical decision;
- support bedside, point-of-care, or live clinical operation;

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.
