# description

该原语用于规划 OpenFold/AF2 风格蛋白结构预测数据链路。决策重点是单体还是多聚体、MSA/template 是否需要现场搜索、是否已有预计算特征，以及输出是否必须进入 OpenFold 模型。

# when_to_use

- 目标模型是 OpenFold 或 AF2 风格模型。
- 输入是 FASTA、mmCIF、PDB、MSA 或 template database。
- 需要生成 OpenFold batch dict。
- 需要多聚体 MSA pairing 或 chain merge。

# inputs

- FASTA 或结构数据路径。
- MSA 数据库和 template 数据库状态。
- 单体/多聚体任务类型。
- OpenFold data config。
- 是否已有预计算 MSA 或特征。
- 训练、验证、推理阶段需求。

# outputs

```text
datapipe_choice:
  name: openfold_data_pipeline
  action: run_full_pipeline | use_precomputed_msa | train_datamodule | reject

data_contract:
  input_protocol: fasta | mmcif | precomputed_features
  output_protocol: openfold_feature_dict
  multimer: true | false
  template_required: true | false

risk_flags:
  - missing_msa_database
  - missing_template_database
  - monomer_multimer_protocol_mismatch
  - feature_config_incomplete
```

# procedure

1. 确认下游模型是否是 OpenFold/AF2 协议。
2. 判断单体或多聚体。
3. 检查是否已有 MSA 和 template；没有则规划外部工具和数据库。
4. 选择 `DataPipeline` 或 `DataPipelineMultimer`。
5. 用 `FeaturePipeline` 对齐 tensor feature。
6. 训练场景使用 DataModule 组织 dataloader。
7. 小样本验证 feature keys、shape 和 crop 设置。

# constraints

- 不要把 Protenix JSON 输入直接送入 OpenFold pipeline。
- 不要混用单体和多聚体 transform。
- 不要在缺少数据库时承诺完整 MSA/template 特征。
- template 日期过滤和 PDB 映射必须与任务设置一致。

# next_phase_recommendation

- 推理：生成 MSA/template 后进入 OpenFold forward。
- 训练：构建 DataModule 并校验 crop、msa depth、template 数。
- 数据缺 MSA：先运行 AlignmentRunner 或准备预计算 MSA。
- 多聚体：先单独校验 chain pairing 和 merge 后的特征字段。

# fallback

- MSA 工具不可用：使用预计算 MSA 或 dummy MSA，仅限可接受的场景。
- template 失败：禁用 template 或修复数据库路径。
- feature transform 报错：检查 data_config 与输入 feature keys。
- 多聚体 pairing 失败：退回单链检查每条链的 MSA 和序列一致性。
