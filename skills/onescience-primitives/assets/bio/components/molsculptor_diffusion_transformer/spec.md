# component_info

`molsculptor_diffusion_transformer` 是 MolSculptor 的分子 latent 去噪 transformer，使用 timestep embedding、可选 label embedding、adaLN 条件块和输出层对 latent token 做去噪预测。

# purpose

用于小分子 latent 空间生成或优化，适合 TargetDiff 类分子生成任务的 latent 扩散参考；不直接预测三维配体坐标，也不包含蛋白 pocket 条件图网络。

# input_schema

```text
tokens:
  Tensor[float]: (Batch, Tokens, Channels)

tokens_mask:
  Tensor[bool|int]: (Batch, Tokens)

time:
  Tensor[int|float]: (Batch,)

label:
  optional Tensor[int]: (Batch,)

tokens_rope_index:
  Tensor[int]: (Batch, Tokens)
```

# output_schema

```text
denoised_or_noise_pred:
  Tensor[float]: (Batch, Tokens, Channels)
```

# parameters

- `config.hidden_size`: transformer hidden dimension。
- `config.n_iterations`: 去噪 block 迭代层数。
- `config.time_embedding`: 时间嵌入配置。
- `config.label_embedding`: 标签条件配置。
- `config.dit_block`: attention/transition block 配置。
- `config.dit_output`: 输出层配置。

# key_dependencies

- `diffusion_transformer.py`
- `transformer.py`
- `attention.py`

# usage_and_risks

该模块默认输出与输入 latent channel 相同的 tensor，训练目标需明确是预测噪声、残差还是 x0。若用于 TargetDiff，需要额外接入口袋条件、坐标约束和分子合法性后处理。

# code_references

- `{onescience_path}/onescience/src/onescience/flax_models/MolSculptor/src/model`
