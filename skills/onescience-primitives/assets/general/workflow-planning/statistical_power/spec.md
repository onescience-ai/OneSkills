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

# knowledge_assets

- `references/effect_sizes.md`: effect-size definitions matched to estimands and planned tests.
- `references/closed_form_recipes.md`: common analytical power and sample-size recipes.
- `references/simulation_based_power.md`: simulation planning for clustered, repeated-measure, and nonstandard designs.

The source `power.py` and `simulate_power.py` remain migration candidates because they expose worked Python modules rather than a stable bounded JSON CLI. Use an executor wrapper only after the design, dependency pins, seed policy, and output schema are specified.
