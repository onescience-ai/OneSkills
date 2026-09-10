# typical_workflow

1. Match the task to `general.tools.timesfm_forecasting` by domain, package, workflow, or artifact type.
2. Retrieve the summary content first and inspect `knowledge_assets` when detailed guidance is needed.
3. Bind task-specific inputs, versions, and provenance before choosing an execution route.
4. Hand off computation to a reviewed executor, notebook, or future execution asset.
5. Return outputs with limitations, validation checks, and source assumptions.

# source_usage_signals

- Forecasting any univariate time series (sales, demand, sensor, vitals, price, weather)
- You need zero-shot forecasting without training a custom model
- You want probabilistic forecasts with calibrated prediction intervals (quantiles)
- You have time series of any length (the model handles 1–16,384 context points)
- You need to batch-forecast hundreds or thousands of series efficiently
- You want a foundation model approach instead of hand-tuning ARIMA/ETS parameters

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.

If `metadata.json.source_payloads` is present, treat those files as preserved migration material only. They can inform future executor design, but they must not be run or imported until promoted through an explicit execution-asset whitelist.
