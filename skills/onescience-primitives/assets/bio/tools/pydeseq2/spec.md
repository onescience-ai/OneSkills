# architecture_overview

PyDESeq2 is a bulk RNA-seq differential-expression primitive based on formula-driven generalized linear models. It captures design, contrast, and result interpretation rules rather than executing a custom pipeline.

# input_schema

Typical inputs are raw integer count matrices, matching sample metadata, a design formula, and one or more explicit contrasts.

# output_schema

Expected outputs include fitted result tables, adjusted p-values, log fold changes, optional shrunken coefficients, and exportable CSV or AnnData-style artifacts.

# key_dependencies

- pydeseq2
- pandas
- numpy
- scipy
- formulaic
- formulaic-contrasts

# common_modification_points

- design formula and reference level
- gene and sample filtering thresholds
- explicit contrast definition
- shrinkage choice and ranking metric
- visualization style for volcano or MA plots

# implementation_risks

- Transposed matrices can silently break the analysis.
- Missing or inconsistent metadata invalidates the design matrix.
- Confounded designs need model changes, not a larger p-value threshold.
- This primitive is for replicate-aware bulk analysis, not per-cell marker testing.

# provenance

Distilled from `scientific-agent-skills/skills/pydeseq2` version `1.3`. Execution scripts were not copied.
