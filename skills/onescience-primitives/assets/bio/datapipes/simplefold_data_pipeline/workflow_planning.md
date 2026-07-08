# description

该原语用于规划 SimpleFold 蛋白折叠数据准备。决策重点是输入处于原始结构、已处理结构样本还是预测输入阶段，并选择 mmCIF 预处理、结构 token 化、训练 DataModule 或推理 DataModule。

# when_to_use

- 目标模型是 SimpleFold 或 FoldingDiT 风格蛋白折叠模型。
- 输入是 mmCIF/PDB 结构或 SimpleFold 预测输入。
- 需要结构 token 化和 SimpleFold batch。
- 不需要 OpenFold MSA/template 特征或 Protenix ligand-rich JSON。

# inputs

- 结构文件路径或 PDB/mmCIF 标识。
- 是否已有预处理样本。
- 训练或推理阶段。
- 链选择、过滤和输出目录。
- 下游模型期望的 `feats` 字段。

# outputs

```text
datapipe_choice:
  name: simplefold_data_pipeline
  action: preprocess_mmcif | tokenize_structure | training_datamodule | inference_datamodule | reject

data_contract:
  input_protocol: mmcif | pdb | processed_structure
  output_protocol: simplefold_sample
  requires_msa: false

risk_flags:
  - structure_parse_failed
  - missing_atoms
  - unsupported_nonstandard_residue
  - datamodule_config_mismatch
```

# procedure

1. 判断目标模型是否为 SimpleFold。
2. 判断输入是否需要先做 mmCIF 预处理。
3. 对单样本执行结构加载和 token 化。
4. 检查输出 sample 字段是否满足模型需求。
5. 训练阶段接入 `SimpleFoldTrainingDataModule`。
6. 推理阶段接入 `SimpleFoldInferenceDataModule`。

# constraints

- 不要用该原语替代 OpenFold 的 MSA/template pipeline。
- 不要把 Protenix JSON 直接送入 SimpleFold pipeline。
- 原始结构质量不足时必须先清洗或过滤。
- 训练数据目录必须与 DataModule 预期布局一致。

# next_phase_recommendation

- 单样本推理：先完成结构 token 化，再接模型预测。
- 训练：先批量预处理 mmCIF 并生成 split。
- 结构质量问题：先运行结构解析和缺失字段统计。
- 需要 ligand/核酸复合物：考虑 Protenix 或 Boltz 风格 pipeline。

# fallback

- mmCIF 解析失败：转换格式或检查链/残基记录。
- token 化失败：过滤非标准残基或补结构字段。
- DataModule 失败：回退到单样本 dataset 调试路径。
- 下游字段不匹配：检查 SimpleFold 模型版本和数据配置。
