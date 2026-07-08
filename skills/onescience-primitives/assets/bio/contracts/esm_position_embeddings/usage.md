# launch

Python API 方式调用，通常由 ESM 模型内部创建：

```sh
python -c "from onescience.modules.esm.embeddings import LearnedPositionalEmbedding, SinusoidalPositionalEmbedding; print(LearnedPositionalEmbedding.__name__, SinusoidalPositionalEmbedding.__name__)"
```

# input_schema

准备蛋白 token tensor，并设置 padding token。learned embedding 需要确保最大位置小于 `num_embeddings`；sinusoidal embedding 可根据序列长度扩展缓存。

# runtime_interfaces

- `LearnedPositionalEmbedding.forward`: 根据 token mask 生成位置 id 并查表。
- `SinusoidalPositionalEmbedding.forward`: 生成或复用正弦位置表。

# main_functions

- `forward`

# execution_resources

资源消耗很低，主要占用位置表参数和缓存；实际内存由 batch size、序列长度和 embedding dimension 决定。

# operation_limits

不处理三维坐标、MSA pair 表征或分子图。padding_idx 配置错误会使位置编号整体偏移；learned embedding 长度不足会越界。
