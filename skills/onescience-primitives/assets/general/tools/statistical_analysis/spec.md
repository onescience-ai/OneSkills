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

# knowledge_assets

- `references/test_selection_guide.md`: map design and variable structure to tests or models.
- `references/assumptions_and_diagnostics.md`: diagnostic checks and remedial choices.
- `references/effect_sizes_and_power.md`: effect-size, interval, and sensitivity reporting.
- `references/bayesian_statistics.md`: Bayesian alternatives, priors, posterior summaries, and diagnostics.
- `references/reporting_standards.md`: reproducible statistical reporting requirements.

The source `assumption_checks.py` remains a migration candidate because it is a library-style module with plotting side effects and no stable structured CLI contract. References are read-only and do not grant execution permission.
