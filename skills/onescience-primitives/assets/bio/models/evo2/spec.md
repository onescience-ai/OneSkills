# architecture_overview

Evo2 模型资源以 `onescience.models.evo2.models.mamba.MambaModel` 为核心。该类继承 Megatron Core `GPTModel`，将 token embedding、Mamba decoder 与输出层组织为长序列语言模型；`Evo2StyleMCoreMambaModel` 扩展了带 `loss_mask` 的重加权训练损失，`mamba_forward_step` 定义训练 batch 到模型参数的标准映射。

# parameter_scale

- `get_inference_wrapper` 的 `inference_max_seq_length` 默认是 `8192`。
- 层数、hidden size、state-space 与并行配置由 Megatron/Mamba config 决定。
- `HybridMambaConfig8BEvo2Loss` 是源码提供的配置类之一；实际构建必须以选择的配置和 checkpoint 为准。

# architecture_structure

```text
FASTA or token records
  -> tokenizer / FASTA dataset
  -> input_ids + position_ids
  -> token embedding
  -> Mamba decoder stack
  -> output layer
  -> logits, or loss when labels are provided
```

训练时 `mamba_forward_step` 从 batch 读取 `tokens`、`position_ids`、`labels` 与 `loss_mask`；推理可通过 `get_inference_wrapper` 建立 Megatron inference wrapper。

# input_schema

- `forward(input_ids, position_ids, attention_mask=None, labels=None, decoder_input=None, inference_context=None, packed_seq_params=None, inference_params=None, runtime_gather_output=None, loss_mask=None)`。
- 提供 `decoder_input` 时，`input_ids` 与 `position_ids` 被忽略。
- `mamba_forward_step` 期望 batch 至少包含 `tokens`、`position_ids`、`labels`、`loss_mask`。
- FASTA 输入需要先通过 `data/fasta_dataset.py` 与 `data/tokenizer.py` 转为模型张量。

# output_schema

- `labels is None` 时返回底层模型输出，通常是 token logits 或配置指定的 hidden output。
- 提供 `labels` 时返回语言模型损失；Evo2 扩展实现会结合 `loss_mask` 计算重加权损失。
- inference wrapper 的返回协议由 Megatron Core wrapper 管理。

# shape_transformations

1. DNA token ids 与 position ids 进入 embedding。
2. embedding 沿 sequence 维通过 Mamba decoder。
3. post-process 输出 vocabulary 维 logits。
4. 有 labels 时按 token 对齐计算损失，并由 `loss_mask` 排除无效位置。

# key_dependencies

- `evo2_mamba`

# common_modification_points

- 更换 tokenizer 或 vocabulary 时同步修改 embedding、输出层和 checkpoint。
- 调整上下文长度时同步检查数据切片、position ids、推理 wrapper 和并行内存。
- 训练代码复用 `mamba_forward_step` 的 batch 字段，避免自定义字段漂移。
- 推理代码根据 checkpoint 的并行配置构建模型，不把单卡假设写入模型资源。

# implementation_risks

- NeMo、Megatron Core、BioNeMo 与 checkpoint 版本需要匹配。
- `labels` 与 `loss_mask` 必须与 token 序列对齐；offset 错误会产生无效训练目标。
- `decoder_input` 分支会绕过 token embedding，错误同时传参可能掩盖输入问题。
- 超长序列的显存和并行需求由配置决定，不能只修改 wrapper 的最大长度。

# code_references

- `{onescience_path}/onescience/src/onescience/models/evo2/models/mamba.py`
- `{onescience_path}/onescience/src/onescience/models/evo2/data/fasta_dataset.py`
- `{onescience_path}/onescience/src/onescience/models/evo2/data/tokenizer.py`
- `{onescience_path}/onescience/src/onescience/models/evo2/utils/config.py`
