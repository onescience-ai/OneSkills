# launch

Python API 方式调用，通常由 ESM attention 内部使用：

```sh
python -c "from onescience.modules.attention.esm_rotary_embedding import RotaryEmbedding; print(RotaryEmbedding.__name__)"
```

# input_schema

准备 query/key tensor，最后一维为 head dimension，序列维长度用于生成 cos/sin 缓存。

# runtime_interfaces

- `RotaryEmbedding.forward`: 返回应用旋转位置编码后的 tensor。
- `apply_rotary_pos_emb`: 对输入应用 cos/sin 旋转。
- `rotate_half`: 对最后一维做半维旋转。

# main_functions

- `forward`
- `apply_rotary_pos_emb`
- `rotate_half`

# execution_resources

资源消耗很低；主要开销为 cos/sin 缓存和逐元素旋转。

# operation_limits

head dimension 需要满足旋转拆分要求；缓存长度小于输入序列长度时需要重新生成。该模块不能独立替代 attention。
