# component_info

`ptdit_structure_transformer` 是 PT-DiT 的结构表征辅助模块族，包含归一化、transition、outer product 和 outer difference，用于更新 protein single/pair 表征。

# purpose

用于蛋白 residue 表征到 pair 表征的构造和非线性更新，适合结构感知 transformer trunk；不独立执行扩散采样，也不输出原子坐标。

# input_schema

```text
single representation:
  s_i: (Batch, Residues, Channels)
  s_j: (Batch, Residues, Neighbors, Channels)

pair representation:
  z_ij: (Batch, Residues, Neighbors, PairChannels)

masks:
  m_i: (Batch, Residues)
  m_j: (Batch, Residues, Neighbors)
```

# output_schema

```text
updated pair or single representation:
  Tensor[float]: same leading shape, configured output channel
```

# parameters

- `norm_method`: `layernorm` 或 `rmsnorm`。
- `transition_factor`: FFN/GLU 扩展倍率。
- `method`: `ffn` 或 `glu`。
- `outerproduct_dim`: outer product 中间维度。
- `outerdiff_dim`: outer difference 中间维度。
- `output_dim`: pair 输出维度。

# key_dependencies

- `transformer.py`
- `dense.py`
- `utils.py`

# usage_and_risks

OuterProduct 和 OuterDifference 对 residue/neighborhood 维度顺序敏感，mask 广播错误会污染 pair 更新。该模块不包含完整 PT-DiT block，需要与 attention 和 diffusion transformer 联用。

# code_references

- `{onescience_path}/onescience/src/onescience/flax_models/Pt_DiT/module`
