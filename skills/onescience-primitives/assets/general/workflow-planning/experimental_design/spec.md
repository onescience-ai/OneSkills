# architecture_overview

Experimental design is a pre-data-collection planning primitive. It helps choose the allocation, blocking, factor structure, and run order that make downstream inference defensible.

# input_schema

Typical inputs are the research question, treatment arms or factor ranges, response variables, randomization unit, blocking variables, practical constraints, and planned analysis objective.

# output_schema

Expected outputs include a design recommendation, allocation or run-order plan, blocking and stratification logic, replication-level statement, and analysis handoff notes.

# key_dependencies

- optional numpy and pandas for layout generation
- optional DOE tooling when an executor later materializes a design matrix
- statistical-power for sample-size planning
- statistical-analysis for post-collection inference

# common_modification_points

- independent unit of randomization
- blocking or stratification factors
- full vs fractional-factorial design
- response-surface design choice
- crossover, repeated-measures, split-plot, or cluster structure
- plate or batch layout constraints

# implementation_risks

- A confounded design cannot be rescued by later analysis.
- Pseudoreplication invalidates nominal sample sizes.
- Low-resolution fractional designs can alias main effects and interactions.
- Run order can become confounded with drift unless randomized or blocked.

# provenance

Distilled from `scientific-agent-skills/skills/experimental-design` version `1.1`. Scripts were not copied.

# knowledge_assets

- `references/design_types.md`: design-family selection and estimand alignment.
- `references/factorial_and_doe.md`: factorial, fractional-factorial, screening, and response-surface planning.
- `references/randomization_and_blocking.md`: allocation, blocking, stratification, and run-order controls.
- `references/sequential_and_adaptive.md`: interim decisions, stopping rules, and adaptive-design safeguards.

These files are read-only knowledge assets. Their paths and SHA-256 values are declared in `metadata.json`; they do not grant permission to execute source scripts.
