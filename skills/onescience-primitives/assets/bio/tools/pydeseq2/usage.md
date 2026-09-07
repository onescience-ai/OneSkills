# typical_installation

```bash
uv pip install pydeseq2==0.5.4
```

# common_usage

```python
import pandas as pd
from pydeseq2.dds import DeseqDataSet
from pydeseq2.default_inference import DefaultInference
from pydeseq2.ds import DeseqStats

counts = pd.read_csv("counts.csv", index_col=0).T
meta = pd.read_csv("metadata.csv", index_col=0)
dds = DeseqDataSet(counts=counts, metadata=meta, design="~condition", refit_cooks=True, inference=DefaultInference())
dds.deseq2()
ds = DeseqStats(dds, contrast=["condition", "treated", "control"], inference=DefaultInference())
ds.summary()
```

# usage_notes

- Use raw integer counts, not normalized values.
- Make the reference level explicit before fitting.
- Use shrunken coefficients only for ranking and visualization.
- Export result tables for downstream review or reporting.
