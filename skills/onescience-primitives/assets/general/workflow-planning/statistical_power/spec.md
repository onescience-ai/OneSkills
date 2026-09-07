# architecture_overview

Statistical power is a planning primitive that translates a chosen design and target effect into sample-size or sensitivity requirements.

# input_schema

Typical inputs are design type, primary outcome, estimand, effect size, alpha, target power, group ratio, number of groups, repeated-measure structure, multiplicity, and expected attrition.

# output_schema

Expected outputs include required sample size, detectable effect, assumptions, attrition-adjusted target, and limitations of the calculation.

# key_dependencies

- statsmodels or equivalent power-analysis library
- effect-size definition matched to the planned test
- experimental_design primitive
- statistical_analysis primitive

# common_modification_points

- one- vs two-sided hypothesis
- alpha and multiplicity correction
- target power
- group allocation ratio
- attrition and missing-data adjustment
- clustered, repeated-measure, or hierarchical design effect

# implementation_risks

- Power is conditional on the design and effect-size definition.
- Observed post-hoc power is not a substitute for a sensitivity analysis.
- Clustered and repeated-measure studies need the correct effective sample size.
- Inflated sample-size precision can hide uncertain planning assumptions.

# provenance

Distilled from `scientific-agent-skills/skills/statistical-power` version `1.1`. Scripts were not copied.
