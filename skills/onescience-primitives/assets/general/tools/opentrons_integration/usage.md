# typical_workflow

1. Match the task to `general.tools.opentrons_integration` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- opentrons==9.1.1 for reproducible Flex simulation.
- opentrons==9.0.0 for local OT-2 API 2.28 compatibility simulation.
- Flex supports API levels 2.15 through 2.29 on current software.
- OT-2 supports API levels 2.0 through 2.28 on current software.
- API 2.29 is Flex-only at this baseline. Do not put 2.29 in an OT-2 protocol.
- Use Protocol Designer for supported no-code workflows.

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.
