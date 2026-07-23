# launch

ESM 表征模型可直接从本地 checkpoint 加载，使用包内 `Alphabet` 完成 token 化：

```sh
python -c "from onescience.models.esm import pretrained; from onescience.models.esm.esm2 import ESM2; import inspect; print(inspect.signature(pretrained.load_model_and_alphabet_local)); print(inspect.signature(ESM2)); print(inspect.signature(ESM2.forward)); print(inspect.signature(ESM2.predict_contacts))"
```

# input_schema

- `checkpoint_path`：本地 ESM/ESM2/MSA Transformer/ESMFold/inverse-folding 权重。
- `sequence_records`：`[(id, amino_acid_sequence), ...]`；普通 ESM token tensor 为 `(batch, tokens)`。
- `repr_layers` 选择返回层；`return_contacts=True` 额外返回残基接触概率。
- ESMFold 接收单条或批量氨基酸序列并输出 atom 坐标、pLDDT、PAE 等结构字段；`infer_pdb` 返回 PDB 文本。
- inverse folding 接收 backbone 坐标 `(L, 3, 3)`、可选 partial sequence、confidence 和 temperature，输出采样序列或序列分数。

# runtime_interfaces

- `pretrained.load_model_and_alphabet_local(path)`：从本地权重恢复模型和 alphabet。
- `Alphabet.get_batch_converter()`：把蛋白序列转换为 token batch。
- `ESM2.forward(tokens, repr_layers, return_contacts)`：输出 logits、representations、attentions/contacts。
- `ESM2.predict_contacts(tokens)`：直接生成 contact map。
- `ESMFold.infer`、`infer_pdb`：单序列结构推理。
- `GVPTransformerModel.sample`、`score_sequence`：结构条件序列生成与评分。

# main_functions

- `load_model_and_alphabet_local`
- `forward`
- `predict_contacts`
- `infer`
- `infer_pdb`
- `sample`
- `score_sequence`

# execution_resources

- 需要模型权重、PyTorch 与相应结构依赖；表征提取和 ESMFold 推荐 GPU。
- FASTA、单序列或 MSA 转 token batch 时，召回 datapipe 资源 `esm_sequence_batch_converter`。
- 长序列应控制 token batch、截断策略与 ESMFold chunk size。
- 训练代码可直接复用模型 logits 和 token mask 构建 masked-language-model loss；结构训练需额外数据与损失契约。

# operation_limits

- 输入必须是蛋白氨基酸或蛋白 backbone，不处理 DNA/RNA 基因组序列。
- 表征、ESMFold 与 inverse-folding checkpoint 的 alphabet 和模型类不可混用。
- ESMFold 是单序列折叠路线，不等同于完整 MSA/template 结构协议。
- inverse folding 只生成/评分序列，不提供 backbone 生成能力。
