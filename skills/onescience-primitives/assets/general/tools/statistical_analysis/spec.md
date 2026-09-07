# architecture_overview

Statistical analysis is a cross-domain tool primitive for choosing and reporting defensible analyses. It is not a single library; it binds the analysis question to appropriate statistical methods and implementation tools.

# input_schema

Typical inputs are an analysis table, outcome and predictor variables, grouping or repeated-measure structure, planned hypothesis, alpha or interval policy, and reporting target.

# output_schema

Expected outputs include selected test or model, assumption diagnostics, effect sizes, intervals, p-values or posterior summaries, and a reproducible reporting summary.

# key_dependencies

- scipy
- statsmodels
- pingouin
- pandas
- matplotlib or seaborn for diagnostics
- pymc and arviz for Bayesian alternatives

# common_modification_points

- parametric vs non-parametric test
- paired, independent, blocked, nested, or repeated-measure design
- variance and normality remedies
- multiple-comparison correction
- robust or Bayesian alternative
- report format

# implementation_risks

- Choosing tests after seeing results invalidates confirmatory p-values.
- Missing design structure can make the wrong unit of analysis look precise.
- Effect sizes and intervals are required for meaningful interpretation.
- Post-hoc observed power is usually misleading; use sensitivity analysis instead.

# provenance

Distilled from `scientific-agent-skills/skills/statistical-analysis` version `1.1`. Scripts were not copied.
