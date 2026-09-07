# architecture_overview

scVelo is a trajectory-direction primitive built on spliced and unspliced counts. It augments Scanpy-style preprocessing with velocity-aware state transition estimates.

# input_schema

Typical inputs are AnnData objects with `layers["spliced"]` and `layers["unspliced"]`, plus a neighbor graph or UMAP embedding for visualization.

# output_schema

Expected outputs include velocity layers, velocity graphs, latent time, velocity pseudotime, driver-gene tables, and velocity embeddings.

# key_dependencies

- scvelo
- scanpy
- anndata
- numpy
- pandas
- matplotlib

# common_modification_points

- stochastic vs dynamical velocity model
- `n_neighbors` and `n_pcs`
- `min_shared_counts` and gene filtering
- `recover_dynamics` budget
- choice of basis and visualization style

# implementation_risks

- Missing spliced or unspliced layers makes the primitive unusable.
- Random-looking arrows usually indicate poor preprocessing or an unsuitable neighborhood graph.
- Some code paths are sensitive to package-version combinations.
- Velocity is directional evidence, not a substitute for biological validation.

# provenance

Distilled from `scientific-agent-skills/skills/scvelo` version `1.2`. Execution scripts were not copied.
