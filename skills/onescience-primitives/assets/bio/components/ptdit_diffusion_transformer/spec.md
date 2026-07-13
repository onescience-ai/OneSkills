# component_info

`ptdit_diffusion_transformer` 是 PT-DiT 的蛋白 latent diffusion transformer，通过时间嵌入、标签条件、adaLN、attention block 和 transition block 在 ProToken latent token 空间进行去噪预测。

# purpose

用于蛋白序列-结构联合 latent 生成、补全和编辑，适合 LaProteina 类蛋白生成任务参考；不直接读取 PDB，也不输出最终原子坐标。

# input_schema

```text
tokens:
  Tensor[float]: (Batch, ResiduesOrTokens, Channels)

tokens_mask:
  Tensor[bool|int]: (Batch, ResiduesOrTokens)

time:
  Tensor[int|float]: (Batch,)

label:
  optional Tensor[int]: (Batch,)

tokens_rope_index:
  Tensor[int]: (Batch, ResiduesOrTokens)
```

# output_schema

```text
predicted latent:
  Tensor[float]: (Batch, ResiduesOrTokens, Channels)
```

# parameters

- `hidden_size`: transformer hidden dimension。
- `n_iterations`: block 数量。
- `emb_label_flag`: 是否启用标签条件。
- `label_drop_rate`: classifier-free guidance 标签 dropout。
- `dit_block`: attention/transition 配置。
- `dit_output`: 输出投影配置。

# key_dependencies

- `diffusion_transformer.py`
- `attention.py`
- `transformer.py`

# usage_and_risks

蛋白序列长度通常需要按 attention 实现要求 padding；若和 ProToken codebook 联用，latent channel 和 token mask 必须完全一致。该模块只是 denoiser，采样循环和结构解码需要外部组件提供。

# code_references

- `{onescience_path}/onescience/src/onescience/flax_models/Pt_DiT/model`
