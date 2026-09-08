# typical_workflow

1. Match the task to `general.workflow-planning.hypothesis_generation` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- present a hypothesis, mechanism, causal effect, citation, or apparent pattern as established evidence;
- claim novelty because a quick search found nothing;
- infer causation from association, temporal order alone, predictive accuracy, or model output;
- supply patient-specific diagnosis, treatment, dose, prognosis, or other clinical advice;
- provide harmful experimental optimization or operational detail for pathogens, toxins, weapons, evasion, or other misuse;
- bypass IRB/REC, IACUC, IBC, biosafety, dual-use, privacy, legal, or regulatory review;

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.
