# when_to_use

Use this primitive when a task involves group comparison, hypothesis testing, regression, correlation, assumption checks, effect size reporting, or Bayesian alternatives.

# when_not_to_use

- Use experimental_design before data are collected and the design is still being chosen.
- Use a domain-specific primitive for specialized omics, CFD, climate, or materials analysis when method assumptions are domain-specific.
- Use a low-level model primitive if the statistical method is already fixed.

# planning_steps

1. Lock the hypothesis, outcome, predictors, and unit of analysis.
2. Inspect data structure and missingness.
3. Choose the test or model from the design.
4. Check assumptions and document remedial choices.
5. Return effect sizes, intervals, exact statistics, and reporting text.

# fallback

- If design metadata are missing, produce a required-fields checklist.
- If assumptions fail, route to robust, non-parametric, or Bayesian alternatives.
- If analysis is underpowered, report a sensitivity analysis rather than observed power.

# handoff_notes

Include variable names, design structure, planned test/model, assumption checks, correction policy, and output report format.

# resource_retrieval_notes

Retrieve the indexed guides before selecting a test or reporting result details. Separate source-backed method guidance from computed output, and record the package or executor used for any numeric result.
