# typical_workflow

1. Match the task to `bio.tools.pyopenms` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- Feature finding: FeatureFinder("centroided") was removed. Use
- idXML I/O: IdXMLFile().load/store require a ms.PeptideIdentificationList()
- Adduct decharging: the class is MetaboliteFeatureDeconvolution, and adducts
- DataFrame columns: FeatureMap.get_df() uses lowercase rt/mz (not RT).
- Bundled data caveat: the pip wheel ships HMDBMappingFile.tsv but not
- MSExperiment – collection of spectra and chromatograms

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.
