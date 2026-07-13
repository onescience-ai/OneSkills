# component_info

`esm_lm_contact_heads` 是 ESM 输出头组件，包含 `RobertaLMHead` 和 `ContactPredictionHead`，分别进行 masked token 预测和残基接触概率预测。

# purpose

用于 ESM 预训练/评估阶段的序列 token 恢复和接触图估计。适合蛋白语言模型下游分析；不适合直接作为配体亲和力评分头或分子扩散头。

# input_schema

```text
LM head:
  features: Tensor[float]: (Batch, Length, EmbedDim)

Contact head:
  attentions: Tensor[float]: layer/head attention maps
  tokens: Tensor[int]: (Batch, Length)
```

# output_schema

```text
LM logits:
  Tensor[float]: (Batch, Length, VocabSize)

contact probabilities:
  Tensor[float]: (Batch, Length, Length)
```

# parameters

- `embed_dim`: 输入特征维度。
- `output_dim`: 词表大小。
- `weight`: 可选共享 embedding 权重。
- `prepend_bos` / `append_eos`: contact head 的特殊 token 处理。
- `eos_idx`: 结束 token 编号。

# key_dependencies

- `heads.py`
- `functional.py`
- `layer_norm.py`

# usage_and_risks

contact head 依赖模型 attention map，不能只输入最终 hidden states；特殊 token 裁剪配置错误会导致接触图偏移。LM head 的输出 token 空间必须与 tokenizer 词表一致。

# code_references

- `{onescience_path}/onescience/src/onescience/modules/esm`
