# component_info

`esm_rotary_embedding` 是 ESM attention 的旋转位置编码辅助组件，提供 `rotate_half`、`apply_rotary_pos_emb` 和 `RotaryEmbedding`，用于对 query/key 注入连续位置相位。

# purpose

用于增强 ESM 多头注意力对相对位置的表达，适合蛋白序列 transformer 或 inverse folding decoder；不单独产生 token 表征，也不处理 MSA row/column attention。

# input_schema

```text
attention tensor:
  Tensor[float]: (..., SeqLen, HeadDim)

cos/sin cache:
  Tensor[float]: compatible with SeqLen and HeadDim
```

# output_schema

```text
rotated tensor:
  Tensor[float]: same shape as input
```

# parameters

- `dim`: head dimension。
- `base`: 频率基数，默认常见值为 10000。
- `precision`: 频率缓存精度。

# key_dependencies

- `esm_rotary_embedding.py`

# usage_and_risks

要求最后一维可按旋转规则拆成两半；缓存长度不足时需要更新频率表。该组件必须嵌入 attention 调用链，单独使用不会完成蛋白序列表征。

# code_references

- `{onescience_path}/onescience/src/onescience/modules/attention`
