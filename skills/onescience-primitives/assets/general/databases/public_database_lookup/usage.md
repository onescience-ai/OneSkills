# typical_workflow

1. Match the task to `general.databases.public_database_lookup` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- A Europe PMC id is not unique on its own. MED/32117569 and PPR1283561 are {source}/{id} pairs; carry the source.
- Custom headers. Semantic Scholar authenticates with x-api-key: $S2_API_KEY; CORE uses Authorization: Bearer $CORE_API_KEY.
- POST bodies. Semantic Scholar's /paper/batch and /recommendations/papers/ endpoints, and CORE's complex search, are POST with a JSON body.
- Seeing the real failure. These APIs signal failure inside a 200 body. curl shows you the body and the status; a tool that summarizes prose hides both.
- Serialize requests to rate-limited APIs. NCBI (PubMed, PMC): 3 req/s without key, 10 with. arXiv: 1 request per 3 seconds — be patient. Crossref: 5 req/s public, 10 with mailto.
- On HTTP 429/503, wait briefly and retry once. Semantic Scholar without a key hits this often — one retry, then tell the user a key would help.

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.

If `metadata.json.source_payloads` is present, treat those files as preserved migration material only. They can inform future executor design, but they must not be run or imported until promoted through an explicit execution-asset whitelist.
