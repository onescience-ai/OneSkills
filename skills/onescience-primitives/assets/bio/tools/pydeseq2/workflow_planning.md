# when_to_use

Use this primitive when a task needs replicate-aware bulk RNA-seq differential expression with a formula-based design and explicit contrast.

# when_not_to_use

- Use Scanpy for per-cell exploratory marker testing.
- Use scvi-tools for probabilistic single-cell modeling.
- Use a conversion primitive if the task is only about reading or reshaping a matrix.

# planning_steps

1. Confirm that the counts matrix is raw and oriented as samples by genes.
2. Choose the design formula and reference level.
3. Filter weakly expressed genes and invalid samples.
4. Fit the model and test the desired contrast.
5. Apply shrinkage only for ranking or visualization.

# fallback

- If the design is confounded, simplify the formula or switch to a different statistical plan.
- If the input is transposed, correct the orientation before fitting.
- If the task is not replicate-aware bulk DE, route it to the appropriate single-cell or model primitive.

# handoff_notes

Include the count matrix path, sample metadata path, design formula, contrast, and any filtering thresholds.
