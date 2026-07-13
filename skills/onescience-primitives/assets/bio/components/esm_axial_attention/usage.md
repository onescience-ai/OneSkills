# launch

Python API 方式调用，通常由 MSA Transformer 层内部使用：

```sh
python -c "from onescience.modules.attention.esm_axial_attention import RowSelfAttention, ColumnSelfAttention; print(RowSelfAttention.__name__, ColumnSelfAttention.__name__)"
```

# input_schema

准备 MSA activation，维度按 `(Rows, Cols, Batch, Channels)` 组织；同时准备 padding mask 或 attention mask，保证行列方向 mask 与 activation 对齐。

# runtime_interfaces

- `RowSelfAttention.forward`: 沿 MSA row 方向计算注意力。
- `ColumnSelfAttention.forward`: 沿 MSA column 方向计算注意力。
- `compute_attention_update`: 在大 MSA 时分块计算更新。

# main_functions

- `forward`
- `compute_attention_update`

# execution_resources

大 MSA 对显存敏感；行注意力和列注意力复杂度不同，可通过 token 阈值触发分块策略。

# operation_limits

输入布局不同于 batch-first transformer；mask 维度错误会造成 shape mismatch 或注意力泄漏。不适合直接编码单个小分子图。
