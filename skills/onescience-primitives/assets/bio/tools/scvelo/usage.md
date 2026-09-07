# typical_installation

```bash
uv pip install scvelo
```

# common_usage

```python
import scvelo as scv
import scanpy as sc

adata = scv.read("velocyto.loom")
scv.pp.filter_and_normalize(adata, min_shared_counts=20)
sc.pp.log1p(adata)
sc.pp.neighbors(adata, n_neighbors=30, n_pcs=30)
scv.pp.moments(adata, n_pcs=30, n_neighbors=30)
scv.tl.velocity(adata, mode="dynamical")
scv.tl.velocity_graph(adata)
scv.tl.latent_time(adata)
```

# usage_notes

- Use a Scanpy-preprocessed AnnData object when possible.
- Start with the stochastic model for exploration; move to the dynamical model for publication-quality directionality.
- Verify arrows and latent-time ordering against known biology.
- Keep spliced and unspliced layers intact when handing the object to downstream tools.
