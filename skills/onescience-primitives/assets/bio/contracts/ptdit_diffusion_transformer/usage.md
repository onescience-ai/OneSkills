# launch

Python API 方式调用，作为 PT-DiT denoiser 使用：

```sh
python -c "from onescience.flax_models.Pt_DiT.model.diffusion_transformer import DiffusionTransformer; print(DiffusionTransformer.__name__)"
```

# input_schema

准备 ProToken latent tokens、tokens_mask、time、可选 label 和 tokens_rope_index。序列长度需要按 attention 配置进行 padding。

# runtime_interfaces

- `DiffusionTransformer.__call__`: 根据 timestep 和条件预测 latent 更新。
- `TimestepEmbedder.__call__`: 构造时间嵌入。
- `LabelEmbedder.__call__`: 构造标签或 classifier-free guidance 条件。
- `DiffusionTransformerBlock.__call__`: 执行单层 DiT 更新。

# main_functions

- `__call__`
- `timestep_embedding`
- `token_drop`

# execution_resources

适合在加速设备上运行；显存取决于 residue/token 长度、hidden size、层数和 batch size。

# operation_limits

不包含完整采样循环、ProToken 编码或结构解码。label dropout 与 guidance 需要和训练配置一致。
