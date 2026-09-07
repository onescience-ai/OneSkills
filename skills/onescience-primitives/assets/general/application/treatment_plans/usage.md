# typical_workflow

1. Match the task to `general.application.treatment_plans` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- diagnose, assess, classify, or screen a person;
- select, rank, recommend, substitute, or compare therapies;
- choose a medication, dose, route, frequency, duration, or monitoring threshold;
- start, stop, hold, resume, titrate, taper, or deprescribe anything;
- check interactions, allergies, contraindications, organ-function suitability, or treatment eligibility;
- infer missing clinical content, intervals, dates, targets, escalation criteria, or instructions;

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.
