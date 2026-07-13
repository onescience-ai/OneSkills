# component_info

`protoken_vq_decoder` 是 ProToken 的 VQ latent 解码模块，将量化 single latent 恢复为 single/pair 表征，并输出 distogram logits 和 bin edges。

# purpose

用于从结构 token latent 回到蛋白结构表征空间，适合蛋白结构重建和 latent 质量检查；不直接输出 atom 坐标，需要继续调用 protein decoder。

# input_schema

```text
vq_act:
  Tensor[float]: (Batch, Residues, Channels)

seq_mask:
  Tensor[float|bool]: (Batch, Residues)

residue_index:
  Tensor[int]: (Batch, Residues)
```

# output_schema

```text
single_act:
  Tensor[float]: (Batch, Residues, SingleChannels)

pair_act:
  Tensor[float]: (Batch, Residues, Residues, PairChannels)

dist_logits:
  Tensor[float]: (Batch, Residues, Residues, NumBins)

dist_bin_edges:
  Tensor[float]: (NumBins - 1)
```

# parameters

- `pre_layer_norm`: 是否先对 latent 做归一化。
- `pair_update_evoformer_stack_num`: pair 更新层数。
- `single_update_transformer_stack_num`: single 更新层数。
- `co_update_evoformer_stack_num`: 协同更新层数。
- `distogram`: distogram head 配置。

# key_dependencies

- `decoder.py`
- `flash_evoformer.py`
- `transformers.py`
- `head.py`
- `transformer_blocks.py`

# usage_and_risks

`vq_act` 通道数必须与训练时 latent 配置一致；`residue_index` 错误会导致 relative position embedding 错位。该模块不恢复全原子结构，必须与 protein decoder 配合。

# code_references

- `{onescience_path}/onescience/src/onescience/flax_models/protoken/model`
