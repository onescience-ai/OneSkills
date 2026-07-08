# description

该原语用于在任务需要读取蛋白质序列、MSA、结构文件或 Protenix JSON 时，判断是否复用 OneScience 的 biology protein 数据层。规划重点是先区分输入是否为 Protenix JSON，再决定直接使用 `ProtenixInferAdapter`、继承 `ProteinDataset` 增加模型 adapter，还是转向 OpenFold/Protenix 专用 pipeline。

# when_to_use

- 输入是蛋白 FASTA、MSA、PDB、mmCIF、MMTF 或 Protenix JSON。
- 需要建立蛋白或复合物样本索引。
- 下游模型可接受通用 sequence/MSA/structure feature，或需要 Protenix 推理 feature。
- 希望复用 biology 目录的解析、关联、adapter 注册和 DataLoader 入口。

# inputs

- 输入文件类型和目录布局。
- 是否存在 `input_json_path`。
- 是否需要 MSA、结构或多链信息。
- 下游模型期望的 feature dict 字段。
- 是否需要训练路径、推理路径或只做数据检查。

# outputs

```text
datapipe_choice:
  name: biology_protein_dataset
  action: reuse_json_adapter | extend_dataset | use_specialized_pipeline | reject

data_contract:
  sequence_source: fasta | json | mixed
  msa_required: true | false
  structure_required: true | false
  multimer_required: true | false
  output_protocol: protenix_feature | unified_feature | custom_adapter

risk_flags:
  - non_json_getitem_incomplete
  - missing_msa_parser_support
  - structure_feature_not_model_ready
  - adapter_not_registered
```

# procedure

1. 判断输入是否为 Protenix/AF3 JSON；若是，优先选择 `protenix_infer_adapter`。
2. 判断任务是否为多链复合物；若是，优先选择 `MultimerDataset`。
3. 检查 FASTA、MSA、结构文件能否通过文件名或 description 关联。
4. 对齐下游模型 feature 协议，确认是否需要额外 adapter。
5. 若目标是 OpenFold 或 Protenix 训练，优先比较专用 pipeline 是否更合适。
6. 小样本读取并检查返回字段、shape、错误信息。

# constraints

- 不要把当前通用非 JSON 路径当作完整训练 datapipe。
- 不要假设 MSA 搜索或模板搜索会在该原语内部完成。
- 不要把结构 featurizer 输出直接等同于 OpenFold/Protenix batch。
- 若下游需要 batch 合并，必须明确 collate 策略。

# next_phase_recommendation

- Protenix JSON 推理：进入 `biology_protenix_infer_adapter` 或 `protenix_data_pipeline`。
- OpenFold 训练/推理：进入 `openfold_data_pipeline`。
- 普通 FASTA/MSA/结构样本接入新模型：新增最小 adapter 并补齐 `__getitem__`。
- 大规模数据：先生成样本 manifest 和字段校验报告。

# fallback

- JSON adapter 失败：直接检查 JSON schema、实体类型和 Protenix 依赖。
- MSA 解析失败：转换为 A3M 或 Stockholm。
- 结构解析失败：统一转换为 PDB/mmCIF 并检查链 ID。
- 非 JSON 路径不可训练：转为专用模型 pipeline 或实现自定义 dataset adapter。
