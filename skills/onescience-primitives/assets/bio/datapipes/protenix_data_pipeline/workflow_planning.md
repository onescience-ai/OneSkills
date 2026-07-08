# description

该原语用于规划 Protenix/AF3 风格结构预测的数据接入。决策重点是任务属于 JSON 推理、结构训练、蒸馏数据处理还是多数据集采样，并据此选择 inference dataset、adapter、training dataset 或完整 dataloader。

# when_to_use

- 目标模型是 Protenix 或 AF3 风格 Pairformer/扩散结构模型。
- 输入包含蛋白、核酸、ligand、ion 或共价键。
- 需要 Protenix feature dict。
- 需要训练采样、过滤或多数据集权重组合。

# inputs

- 输入协议：JSON、mmCIF、PDB、MSA 或样本清单。
- 实体类型、链数、ligand 和共价键情况。
- CCD/化学依赖可用性。
- 训练或推理阶段。
- 采样权重和过滤规则。

# outputs

```text
datapipe_choice:
  name: protenix_data_pipeline
  action: inference | training_dataloader | json_adapter | reject

data_contract:
  input_protocol: protenix_json | mmcif_dataset | weighted_dataset
  output_protocol: protenix_feature_dict
  supports_ligand: true
  supports_nucleic_acid: true

risk_flags:
  - ccd_missing
  - ligand_parse_failed
  - msa_type_mismatch
  - sampler_config_incomplete
  - openfold_protocol_mismatch
```

# procedure

1. 判断下游是否为 Protenix/AF3 风格模型。
2. 判断任务阶段：推理、训练或数据转换。
3. JSON 推理优先选择 `InferenceDataset` 或 biology adapter。
4. 训练任务检查样本清单、权重、过滤和 MSA 配置。
5. 检查 ligand、ion、非标准残基和共价键是否可解析。
6. 生成小样本 feature 并核对字段。
7. 接入模型训练或推理入口。

# constraints

- 不要将 Protenix feature dict 与 OpenFold feature dict 混用。
- 不要跳过 ligand/CCD 校验。
- 多数据集权重采样必须有明确权重来源。
- RNA MSA 与蛋白 MSA 不能按同一规则处理。

# next_phase_recommendation

- JSON 推理：优先生成 feature 并运行 Protenix inference。
- 训练：先做样本过滤统计和采样权重检查。
- ligand-rich 数据：先做 CCD/SMILES/键合法性校验。
- 与 OpenFold 对比：明确两套 feature 协议转换边界。

# fallback

- JSON 推理失败：转用 `biology_protenix_infer_adapter` 做更小粒度排查。
- ligand 失败：标准化 ligand 或补 CCD。
- MSA 失败：使用 dummy MSA 或重新生成对齐。
- 训练采样失败：先退回单数据集、无权重、无分布式的小样本加载。
