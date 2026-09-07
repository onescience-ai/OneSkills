# when_to_use

Use this primitive when a task needs RNA velocity, latent time, directional trajectory inference, or driver-gene dynamics from single-cell data.

# when_not_to_use

- Use Scanpy for standard clustering and embedding without velocity.
- Use scvi-tools when the main task is probabilistic batch correction or transfer learning.
- Use a data-format primitive when the task is only about AnnData layout or file conversion.

# planning_steps

1. Confirm that spliced and unspliced counts are available.
2. Decide whether the stochastic or dynamical velocity model fits the budget.
3. Run Scanpy preprocessing and compute the neighborhood graph first.
4. Fit velocity, then check latent time and directional plots.
5. Return unresolved or noisy trajectories with evidence instead of inventing fate labels.

# fallback

- If the required layers are missing, request velocyto-style preprocessing or a different input source.
- If the dynamical model is too slow, fall back to stochastic velocity for exploratory work.
- If trajectories remain ambiguous, hand back velocity confidence and marker evidence only.

# handoff_notes

Include the AnnData path, spliced/unspliced layer names, chosen model, neighborhood parameters, and the expected plot outputs.
