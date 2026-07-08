# description

该原语用于规划 ESM 输入 token 化任务。决策重点是判断输入是普通蛋白序列、FASTA 文件还是 MSA，对应选择 BatchConverter、FastaBatchedDataset 或 MSABatchConverter，并确认下游模型是否只需要 ESM token batch。

# when_to_use

- 下游模型是 ESM 或使用 ESM token 协议。
- 输入是蛋白质单序列、FASTA 或 MSA。
- 任务只需要 token ids、labels 和原始序列。
- 需要按 token 数组织 FASTA batch。

# inputs

- 序列来源：内存列表、FASTA 文件或 MSA。
- ESM architecture/alphabet。
- 是否需要 BOS/EOS。
- 最大序列长度或 token budget。
- 下游模型是否需要 MSA 维度。

# outputs

```text
datapipe_choice:
  name: esm_sequence_batch_converter
  action: use_sequence_converter | use_msa_converter | use_fasta_dataset | reject

data_contract:
  input_protocol: sequence_tuple | fasta | msa_tuple
  output_protocol: esm_tokens
  has_msa_dimension: true | false

risk_flags:
  - unsupported_residue
  - msa_length_mismatch
  - sequence_truncated
  - downstream_requires_structure_features
```

# procedure

1. 判断输入是否为 MSA；若是，使用 `MSABatchConverter`。
2. 判断输入是否为 FASTA 文件；若是，使用 `FastaBatchedDataset`。
3. 选择匹配模型的 alphabet。
4. 设置截断长度或 token budget。
5. 转换小批量样本并检查 token shape。
6. 与下游模型输入协议对齐。

# constraints

- 不要把 DNA/RNA 输入送入 ESM 蛋白 alphabet。
- 不要用该原语替代 OpenFold 或 Protenix 的结构特征流水线。
- MSA 内序列必须等长。
- 如果任务需要坐标、模板或 ligand，必须切换到结构 pipeline。

# next_phase_recommendation

- ESM 表征提取：接入 ESM 模型 forward。
- ESMFold/SimpleFold 相关任务：继续进入结构数据或 SimpleFold pipeline。
- 大 FASTA：先用 token budget 生成 batch indices。
- MSA 任务：先检查 MSA 深度和对齐长度。

# fallback

- 非法字符：清理或映射未知残基。
- MSA 不等长：重新对齐或过滤异常行。
- token 数过大：降低 batch size、截断序列或限制 MSA 深度。
- 下游要求结构特征：切换到 `openfold_data_pipeline`、`protenix_data_pipeline` 或 `simplefold_data_pipeline`。
