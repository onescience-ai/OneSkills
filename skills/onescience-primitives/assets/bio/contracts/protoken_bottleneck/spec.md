# component_info

`protoken_bottleneck` 是 ProToken 的表征压缩与量化瓶颈模块，用于把连续蛋白结构表征映射到离散 code 或 compact latent，并为 PT-DiT 等 latent 生成模型提供 token 空间。

# purpose

用于连接结构 encoder 与 decoder，形成可生成、可采样、可重建的 protein structure token。适合蛋白 latent 扩散、结构压缩和 codebook 分析；不单独执行结构预测。

# input_schema

```text
single_act:
  Tensor[float]: residue single representation

mask:
  optional Tensor[float|bool]: residue mask

configuration:
  codebook size, latent dim, quantization mode
```

# output_schema

```text
quantized_act:
  Tensor[float]: quantized latent representation

vq_indexes:
  Tensor[int]: discrete token indexes

auxiliary losses / metrics:
  commitment or codebook usage statistics
```

# parameters

- `codebook_size`: 离散 token 数。
- `latent_dim`: latent 表征维度。
- `commitment_cost`: 量化约束权重。
- `ema_decay`: 可选 codebook 更新衰减。
- `temperature`: 可选软量化温度。

# key_dependencies

- `bottleneck.py`

# usage_and_risks

codebook 训练质量直接影响后续 PT-DiT 生成和 decoder 重建。若 mask、latent dim 或 codebook size 与 checkpoint 不一致，会导致 token index 无效或重建失败。

# code_references

- `{onescience_path}/onescience/src/onescience/flax_models/protoken/model`
