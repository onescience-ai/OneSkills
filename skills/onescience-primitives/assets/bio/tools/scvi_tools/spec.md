# architecture_overview

scvi-tools is a probabilistic modeling primitive for single-cell omics. It augments Scanpy workflows with learned latent spaces, batch correction, multimodal fusion, and uncertainty-aware outputs.

# input_schema

Typical inputs are AnnData or MuData objects with raw counts, batch labels, covariates, and modality-specific fields such as protein, ATAC, or spatial metadata.

# output_schema

Expected outputs include latent representations, normalized expression, batch-corrected embeddings, posterior metrics, label-transfer scores, and model checkpoints.

# key_dependencies

- scvi-tools
- torch
- anndata
- scanpy
- pytorch-lightning
- optional MuData and modality-specific extras

# common_modification_points

- model family selection
- `setup_anndata` or equivalent registration
- batch key and covariate keys
- latent dimension and training schedule
- GPU or CPU execution path
- downstream Scanpy neighbor and visualization settings

# implementation_risks

- Models expect raw counts, not normalized input.
- Model namespace choice matters; the wrong namespace can route to the wrong class.
- Large models may require GPU or memory-aware batching.
- Learned outputs are not a substitute for checking biological validity.

# provenance

Distilled from `scientific-agent-skills/skills/scvi-tools` version `1.1`. Execution scripts were not copied.
