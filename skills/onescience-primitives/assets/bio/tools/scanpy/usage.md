# typical_installation

```bash
uv pip install "scanpy[leiden]"
```

Pin versions in reproducible environments. Add Dask, RAPIDS, Harmony, BBKNN, scVI, or other ecosystem packages only when the plan explicitly requires them.

# typical_workflow

1. Load or convert input data to AnnData.
2. Inspect shape, metadata fields, raw count availability, and existing embeddings or layers.
3. Calculate QC metrics and choose thresholds from the dataset distribution.
4. Filter low-quality cells and genes.
5. Normalize, log-transform, select highly variable genes, and preserve raw counts.
6. Run PCA, construct the neighbor graph, and compute UMAP or t-SNE.
7. Cluster with Leiden at one or more resolutions.
8. Generate exploratory marker tables and plots.
9. Annotate cell types using marker evidence or a validated reference.
10. Save intermediate and final `.h5ad` files plus tables and figures.

# common_commands

```python
import scanpy as sc

adata = sc.read_h5ad("input.h5ad")
adata.var["mt"] = adata.var_names.str.startswith("MT-")
sc.pp.calculate_qc_metrics(adata, qc_vars=["mt"], inplace=True)
sc.pp.filter_cells(adata, min_genes=200)
sc.pp.filter_genes(adata, min_cells=3)
sc.pp.normalize_total(adata, target_sum=1e4)
sc.pp.log1p(adata)
adata.raw = adata
sc.pp.highly_variable_genes(adata, n_top_genes=2000)
adata = adata[:, adata.var.highly_variable].copy()
sc.tl.pca(adata)
sc.pp.neighbors(adata, n_neighbors=10, n_pcs=40)
sc.tl.umap(adata)
sc.tl.leiden(adata, resolution=0.5)
adata.write("processed.h5ad")
```

# limitations

- Treat default QC thresholds as starting points, not universal biological rules.
- Use pseudobulk or replicate-aware methods for condition-level differential expression.
- Record versions, thresholds, metadata fields, and output paths for reproducibility.
- For R-native inputs, convert with validated R tooling before loading into Scanpy.
