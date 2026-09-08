# when_to_use

Use this primitive when planning an experiment, assigning units to groups, avoiding confounding, screening factors, or laying out samples before data are collected.

# when_not_to_use

- Use statistical_analysis after the data have already been collected.
- Use statistical-power when the design is already chosen and only sample size is needed.
- Use a domain-specific primitive when experimental constraints are dominated by a specialized platform.

# planning_steps

1. Identify the independent experimental unit.
2. List treatments, factors, responses, and nuisance variables.
3. Choose the smallest design that estimates the required effects.
4. Randomize within the constraints and document the schedule.
5. Record which downstream model must respect blocks, strata, clusters, or repeated measures.

# fallback

- If the independent unit is unclear, stop at a design checklist.
- If resources are too limited for the desired effects, propose a screening or pilot design.
- If constraints force confounding, surface the limitation before execution.

# handoff_notes

Include the design type, randomization unit, block/strata fields, factor levels, seed policy, and analysis model implications.

# resource_retrieval_notes

Retrieve the indexed reference guides when the design choice, allocation plan, factorial aliasing, or adaptive decision rule needs detailed support. Keep the design recommendation and its assumptions in the main result; do not treat a reference file as an executable allocation schedule.
