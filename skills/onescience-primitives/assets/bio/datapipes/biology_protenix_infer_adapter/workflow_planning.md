# description

该原语用于规划 Protenix JSON 推理输入的特征适配。当用户已有 AF3/Protenix 风格 JSON，并希望走 OneScience Protenix 推理模型时，应优先选择该 adapter；若任务涉及训练、权重采样或完整 Protenix 数据集，则转向 `protenix_data_pipeline`。

# when_to_use

- 输入是 Protenix/AF3 JSON。
- 需要输出 Protenix 推理 feature dict。
- 样本包含蛋白、核酸、ligand、ion 或共价键。
- 用户目标是结构预测推理前的数据准备。

# inputs

- JSON 文件路径。
- JSON 中实体类型和数量。
- 是否包含 ligand、ion、非标准残基或共价键。
- 下游 Protenix 模型期望的 feature 字段。
- CCD/分子依赖是否可用。

# outputs

```text
datapipe_choice:
  name: biology_protenix_infer_adapter
  action: reuse | validate_json | switch_to_protenix_pipeline | reject

data_contract:
  input_protocol: protenix_json
  output_protocol: protenix_feature_dict
  atom_level_output: true
  token_level_output: true

risk_flags:
  - invalid_json_schema
  - unsupported_entity_type
  - missing_ccd_component
  - covalent_bond_index_error
```

# procedure

1. 确认输入不是 FASTA/MSA，而是 Protenix/AF3 JSON。
2. 校验 `sequences` 和实体类型。
3. 检查 ligand、ion、非标准残基是否有可解析 CCD 信息。
4. 检查共价键索引是否指向有效实体和原子。
5. 调用 adapter 生成小样本 feature。
6. 将 feature dict 与 Protenix 推理入口字段对齐。

# constraints

- 不要把该 adapter 用作通用 protein dataset。
- 不要在 JSON schema 未校验时直接进入模型推理。
- 不要把 adapter 输出与 OpenFold batch 混用。
- 训练任务应转向 Protenix 专用 dataset/dataloader。

# next_phase_recommendation

- 推理：接入 Protenix inference dataloader 或模型推理入口。
- JSON 不规范：先生成 JSON 校验和修复报告。
- ligand 失败：补 CCD、SMILES 或标准化 ligand 名称。
- 训练需求：进入 `protenix_data_pipeline`。

# fallback

- adapter 注册失败：检查 `model_name` 是否为 `protenix_infer_adapter`。
- JSON 解析失败：最小化样本并逐实体定位错误。
- CCD 缺失：替换为标准残基/组分，或补充组件定义。
- feature 字段不匹配：转向 Protenix 原生 infer pipeline 排查。
