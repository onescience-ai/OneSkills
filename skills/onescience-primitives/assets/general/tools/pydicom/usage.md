# typical_workflow

1. Match the task to `general.tools.pydicom` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- Work only with local data that the user is authorized to access.
- DICOM metadata, file names, private elements, overlays, structured content,
- Never print Dataset, export full metadata/JSON, or log element values by
- pydicom is a general DICOM framework, not a diagnostic viewer. Pixel output,
- De-identification is profile-, purpose-, recipient-, jurisdiction-, and
- Never claim that a tag-removal script is DICOM PS3.15, HIPAA, GDPR, or other

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.
