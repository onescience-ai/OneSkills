# component_info

`molsculptor_smiles_decoder` 是 MolSculptor 的 SMILES token 解码模块，基于条件向量、序列 token、mask 和位置索引，通过 attention/transition block 输出分子 token logits。

# purpose

用于从图 latent 或生成条件恢复 SMILES 序列，适合小分子重构、生成和候选分子枚举；不直接验证化学合法性，也不计算 docking reward。

# input_schema

```text
seq_tokens:
  Tensor[int]: (Batch, SeqLen)

mask:
  Tensor[bool|int]: (Batch, SeqLen)

rope_index:
  Tensor[int]: (Batch, SeqLen)

cond:
  Tensor[float]: (Batch, PrefixTokens, HiddenDim) or compatible condition
```

# output_schema

```text
logits:
  Tensor[float]: (Batch, SeqLen, VocabSize)
```

# parameters

- `config.dim_feature`: token embedding 维度。
- `config.settings_config.vocab_size`: SMILES 词表大小。
- `config.transformer.n_layers`: decoder 层数。
- `config.num_prefix_tokens`: 条件前缀 token 数。
- `config.hyper_lora_flag`: 是否启用条件低秩适配。

# key_dependencies

- `decoder.py`
- `attention.py`
- `transformer.py`

# usage_and_risks

输入 token 需要包含 BOS/EOS/UNK 的一致编号；生成出的 token 序列仍需反 tokenization、SMILES 标准化和分子合法性过滤。若条件前缀长度或分组参数不整除，会触发断言失败。

# code_references

- `{onescience_path}/onescience/src/onescience/flax_models/MolSculptor/net`
