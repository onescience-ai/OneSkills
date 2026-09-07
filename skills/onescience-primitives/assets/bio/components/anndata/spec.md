# architecture_overview

AnnData is the shared annotated-matrix component primitive for scverse workflows. It describes the in-memory and on-disk container, not a full analysis pipeline.

# input_schema

Typical inputs are h5ad, zarr, CSV/MTX/Loom-style matrices, and preprocessed AnnData objects with obs/var metadata, layers, and embeddings.

# output_schema

Expected outputs include validated AnnData objects, sliced views or copies, concatenated objects, exported h5ad/zarr files, and aligned metadata tables.

# key_dependencies

- anndata
- numpy
- pandas
- scipy
- optional scanpy readers for 10x and other non-native inputs
- optional dask or backed storage for large datasets

# common_modification_points

- backed vs in-memory mode
- sparse vs dense matrix representation
- obs/var index alignment
- layer and raw naming conventions
- concat join and merge strategy
- zarr chunking and compression choice

# implementation_risks

- Views can surprise consumers if copied results are expected.
- Metadata misalignment can silently corrupt downstream analysis.
- Native AnnData is not a substitute for non-native readers such as 10x or Seurat conversion tooling.
- Large matrices may require backed or chunked workflows.

# provenance

Distilled from `scientific-agent-skills/skills/anndata` version `1.1`. Execution scripts were not copied.
