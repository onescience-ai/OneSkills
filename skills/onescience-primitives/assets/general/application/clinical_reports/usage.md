# typical_workflow

1. Match the task to `general.application.clinical_reports` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- diagnose, recommend treatment, choose or change dosing, triage, or provide return precautions;
- interpret images, specimens, raw laboratory results, symptoms, or other clinical observations;
- invent, infer, normalize, “complete,” or silently reconcile observations, results, dates, units, denominators, causality, expectedness, seriousness, outcomes, or conclusions;
- create an individual case safety report from patient-level narrative or decide reportability;
- use real PHI in examples, assets, tests, prompts, logs, or external services;
- call an external LLM, image service, API, or another skill.

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.
