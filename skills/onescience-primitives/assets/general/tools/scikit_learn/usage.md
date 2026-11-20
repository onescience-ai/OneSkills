# typical_workflow

1. **Task and inputs.** The research goal, input schema, label meaning, feature order and package/API version determine the applicable estimator or transformation.
2. **Learning and transformations.** Supervised estimators learn from `fit(X, y)`; preprocessing and unsupervised estimators use their corresponding fit/transform interfaces. Existing references describe classification, regression, clustering, dimensionality reduction, pipelines and parameter selection.
3. **Model use.** `predict` returns labels or values, while classification `predict_proba` columns correspond to `classes_`. Consistent feature order and preprocessing make a persisted model's predictions comparable with its original use.
4. **Persistence and products.** Joblib stores and reloads fitted estimators. Serialized model compatibility is version dependent. Raster applications combine estimator output with rasterio/GDAL spatial metadata and nodata conventions.
5. **Interpretation and resources.** Predictive performance refers to the stated data population and independent evaluation design. CPU RandomForest memory depends on training rows, feature precision, tree nodes and prediction batch size; `n_jobs` controls supported CPU parallelism. This estimator does not require external pretrained weights or GPU memory.

# source_usage_signals

- Building classification or regression models
- Performing clustering or dimensionality reduction
- Preprocessing and transforming data for machine learning
- Evaluating model performance with cross-validation
- Tuning hyperparameters with grid or random search
- Creating ML pipelines for production workflows

# migrated_knowledge

Use `content_request: "参考资料"` to retrieve the indexed source references. Use `content_request: "完整参考资料"` only when detailed source text is needed.

This primitive does not expose execution assets yet. Source scripts remain candidates and must pass allowlist, hash, dependency, and side-effect review before promotion.
