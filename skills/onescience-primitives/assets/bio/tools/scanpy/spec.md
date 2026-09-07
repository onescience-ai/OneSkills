# architecture_overview

Scanpy is a Python analysis toolkit for exploratory single-cell RNA-seq workflows built around AnnData. In OneSkills it is represented as a third-party `tool_primitive`: it gives planners and executors structured knowledge about when and how to use Scanpy, but it does not by itself execute analysis.

# input_schema

Typical inputs are `.h5ad`, 10x Genomics matrix directories or h5 files, loom files, matrix market files, or CSV-like count matrices. The workflow should identify:

- sample and batch metadata fields
- organism and gene naming convention
- raw count layer or matrix source
- QC thresholds
- desired embedding, clustering, marker, annotation, and plot outputs

# output_schema

Expected outputs include processed `.h5ad` files, QC metric tables, QC figures, PCA/UMAP/t-SNE coordinates, cluster labels, exploratory marker tables, annotation fields, pseudobulk count matrices, and plot artifacts.

# key_dependencies

- `scanpy`
- `anndata`
- `numpy`
- `pandas`
- `matplotlib`
- `python-igraph` and `leidenalg` when Leiden clustering is required

# common_modification_points

- mitochondrial, ribosomal, or organism-specific QC gene rules
- `min_genes`, `min_cells`, mitochondrial percentage, total-count, and doublet thresholds
- `target_sum`, highly variable gene settings, number of PCs, and neighbor count
- clustering resolution and annotation mapping
- batch correction strategy and covariates
- figure format, grouping fields, and marker gene panels

# implementation_risks

- Do not interpret per-cell marker-test p-values as rigorous condition-level differential expression between biological replicates.
- Preserve raw counts in `.raw` or a named layer before normalization when downstream tests or plotting need them.
- Convert Seurat or SingleCellExperiment R objects to `.h5ad` before using Scanpy in Python.
- Large objects may require memory planning, sparse matrices, chunking, or out-of-core alternatives.
- This primitive does not ship execution scripts; executor skills must create or call project-local scripts and verify artifacts.

# provenance

Distilled from `scientific-agent-skills/skills/scanpy` version `1.5`. Execution scripts from that source were not copied into this primitive.
