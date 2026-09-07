# typical_installation

```bash
uv pip install scvi-tools
uv pip install "scvi-tools[cuda]"
```

# common_usage

```python
import scanpy as sc
import scvi

scvi.model.SCVI.setup_anndata(adata, layer="counts", batch_key="batch")
model = scvi.model.SCVI(adata)
model.train()
adata.obsm["X_scVI"] = model.get_latent_representation()
adata.layers["scvi_normalized"] = model.get_normalized_expression()
```

# usage_notes

- Use raw counts for registration.
- Keep model outputs in AnnData for downstream Scanpy analysis.
- Choose the model family that matches the modality and task.
- Save checkpoints if retraining would be expensive.
