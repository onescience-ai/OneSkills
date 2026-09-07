# typical_installation

```bash
uv pip install "cellxgene-census==1.17.*"
uv pip install "cellxgene-census[spatial]==1.17.*" "spatialdata[extra]>=0.2.5"
```

# common_usage

```python
import cellxgene_census

with cellxgene_census.open_soma(census_version="2025-11-08") as census:
    obs = cellxgene_census.get_obs(
        census,
        "homo_sapiens",
        value_filter="tissue_general == 'lung' and is_primary_data == True",
        column_names=["cell_type"],
    )
```

# usage_notes

- Always pin the Census version.
- Include `is_primary_data == True` unless duplicates are intentional.
- Select only the columns you need before querying large slices.
- Hand off returned AnnData objects to Scanpy or scvi-tools for downstream analysis.
