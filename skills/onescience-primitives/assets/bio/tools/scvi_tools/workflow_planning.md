# when_to_use

Use this primitive when a task needs probabilistic batch correction, transfer learning, multimodal integration, uncertainty-aware differential expression, or other learned single-cell representations.

# when_not_to_use

- Use Scanpy for standard exploratory preprocessing and clustering.
- Use an AnnData primitive when the task is only about matrix structure or file layout.
- Use a model-specific primitive if the task is narrowly about one trained scvi-tools model family.

# planning_steps

1. Confirm raw count inputs and the modality or batch labels needed for registration.
2. Pick the model family that matches the task and data type.
3. Register the AnnData or MuData object with the correct covariates.
4. Train the model and extract the latent or denoised outputs.
5. Hand the results back to Scanpy or a downstream consumer for visualization or testing.

# fallback

- If the model family is unclear, fall back to a standard Scanpy workflow first.
- If the environment lacks GPU support, use a CPU training path or reduce model size.
- If the data are not raw counts, convert or re-register before training.

# handoff_notes

Include the data modality, raw-count layer, batch and covariate keys, expected model family, and the downstream analysis goal.
