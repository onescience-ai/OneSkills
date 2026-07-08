# launch

Python API 方式调用，通常由 ESM transformer layer 调用：

```sh
python -c "from onescience.modules.attention.esm_multihead_attention import MultiheadAttention; print(MultiheadAttention.__name__)"
```

# input_schema

准备 query、key、value activation，默认布局为 `(Length, Batch, Channels)`；可选传入 `key_padding_mask`、`attn_mask` 和 incremental state。

# runtime_interfaces

- `forward`: 执行 self/cross multi-head attention。
- `reorder_incremental_state`: beam search 或增量解码时重排缓存。
- `upgrade_state_dict_named`: 兼容旧 checkpoint 参数名。

# main_functions

- `forward`
- `reorder_incremental_state`
- `upgrade_state_dict_named`

# execution_resources

显存随 `Length * Length * Heads` 增长；启用 rotary embedding 时额外维护频率缓存。

# operation_limits

`embed_dim` 必须能被 `num_heads` 整除。增量缓存、mask 和 batch 维度不一致会导致输出错误或运行失败。
