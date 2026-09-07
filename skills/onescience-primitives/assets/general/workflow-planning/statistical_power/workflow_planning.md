# when_to_use

Use this primitive when a study needs sample-size planning, minimum detectable effect analysis, or attrition-adjusted recruitment targets.

# when_not_to_use

- Use experimental_design when the allocation and design are not yet chosen.
- Use statistical_analysis after data collection for model fitting and reporting.
- Do not use it to justify post-hoc observed-power claims.

# planning_steps

1. Bind the selected experimental design.
2. Define the primary estimand and effect-size scale.
3. Set alpha, target power, allocation, and multiplicity policy.
4. Adjust for attrition, clustering, or repeated measures.
5. Return assumptions, target N, and sensitivity range.

# fallback

- If the effect size is uncertain, return a sensitivity grid.
- If the design effect is unknown, state the missing parameter instead of using a generic correction.
- If the target outcome is not defined, stop at a planning checklist.

# handoff_notes

Include design type, estimand, effect-size source, alpha, target power, ratio, attrition, multiplicity, and whether N is per group or total.
