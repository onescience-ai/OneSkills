# typical_installation

```bash
uv pip install "anndata==0.12.16"
```

```bash
uv pip install "anndata[dask,lazy]==0.12.16"
```

# common_usage

```python
import anndata as ad
import scanpy as sc

adata = ad.read_h5ad("input.h5ad")
adata.raw = adata.copy()
adata = ad.concat([adata1, adata2], label="batch", keys=["a", "b"], join="inner")
adata.write_h5ad("output.h5ad", compression="gzip")
```

# usage_notes

- Use Scanpy for 10x and other non-native readers.
- Preserve raw counts before filtering when downstream modeling or plotting needs them.
- Use backed mode when the object is too large for memory.
- Keep indices aligned before concatenation or metadata joins.
