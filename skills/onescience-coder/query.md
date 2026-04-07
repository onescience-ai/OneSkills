# Query

Please read:

- `./oneskills/case/first_round_guide.md`
- `./oneskills/task/SKILL.md`

Then handle my task.

Write the task here.

If the task involves a new dataset, please include when possible:

- Dataset README path or key field summary
- The reference example or target model you want to reuse
- Expected delivery scope:
  - `datapipe only`
  - or `datapipe + config + train/inference`
- Where the generated files should go:
  - current case directory
  - or `./onescience/src/onescience/datapipes/...`

If the task is a model comparison or benchmark, please include when possible:

- The list of models to compare
- The datapipe or example you want to reuse
- Whether data split, normalization, and evaluation metrics should stay unified

My main concerns are:

- Whether this plan is reasonable and implementable in the current `OneScience` codebase
- If direct replacement is not possible, what the minimum viable adaptation path is
- Which parts can be reused directly, and which parts need a bridge layer
- Keeping changes scoped to files that are directly related to this task

I have mostly read papers and I am not yet familiar with the code details, so please first translate this request into a clear implementation plan before deciding how to write the code.

Please summarize your thinking first and output it as a structured document.

If we later move into the code generation stage, save the generated files in the current case directory by default.
