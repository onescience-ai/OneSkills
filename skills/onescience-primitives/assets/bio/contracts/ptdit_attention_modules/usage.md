# launch

Python API 方式调用，通常由 PT-DiT transformer 或结构模块调用：

```sh
python -c "from onescience.flax_models.Pt_DiT.module.attention import AttentionKernel, AttentionEmbedding, FlashInvariantPointAttention; print(AttentionKernel.__name__, AttentionEmbedding.__name__, FlashInvariantPointAttention.__name__)"
```

# input_schema

准备 single/pair 表征、mask、可选 neighbor index、RoPE index、旋转矩阵和平移向量。不同 attention 子模块要求不同 shape。

# runtime_interfaces

- `AttentionKernel.__call__`: 执行注意力权重计算和 value 聚合。
- `AttentionEmbedding.__call__`: 生成 q/k/v 和可选 pair embedding。
- `HyperAttentionEmbedding.__call__`: 应用 HAK 或 RoPE。
- `FlashInvariantPointAttention.__call__`: 执行结构感知点注意力。

# main_functions

- `__call__`
- `apply_to_point`
- `apply_rope`

# execution_resources

attention 开销随 residue 数平方增长；flash attention 需要满足设备和 block 配置要求；IPA 额外消耗点坐标和距离特征计算。

# operation_limits

sparse/dense 邻居模式不可混用；rotation、translation、mask、neighbor index 不一致会导致结构注意力无效。
