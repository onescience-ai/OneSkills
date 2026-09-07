# typical_workflow

1. Match the task to `general.tools.simpy` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- Latest stable: SimPy 4.1.2, released on PyPI 2026-05-24; source tag
- Package metadata requires Python >=3.8 and classifies CPython 3.8-3.14
- 4.1.2 adds Python 3.13/3.14 support and modern-interpreter test fixes.
- Upstream and this skill are MIT-licensed.
- env.now: unitless simulation clock; choose and document one unit.
- env.peek(): next event time or infinity.

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.
