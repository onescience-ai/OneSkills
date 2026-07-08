# pipeline_responsibility

为 SimpleFold 蛋白折叠模型准备结构样本和 DataModule。该原语负责 mmCIF 获取/解析/处理、结构输入加载、结构 token 化、样本最终组装，以及训练和预测数据模块组织。

# pipeline_architecture

```text
原始结构
  mmCIF / PDB / structure input

预处理
  process_mmcif.py
    -> fetch
    -> parse
    -> process_structure
    -> finalize

结构样本处理
  process_structure.py
    -> load_input
    -> tokenize_structure
    -> finalize
  ProteinDataProcessor
    -> 蛋白结构样本处理

训练
  SimpleFoldTrainingDataset
    -> SimpleFoldTrainingDataModule

推理
  SimpleFoldPredictionDataset
    -> SimpleFoldInferenceDataModule

输出
  SimpleFold 模型所需结构特征和 batch
```

# data_loading

- `process_mmcif.py` 支持获取、解析和处理 mmCIF。
- `process_structure.py` 加载结构输入并转换为内部 sample。
- train/test datamodule 从配置的数据路径读取已处理样本或预测输入。
- `ProteinDataProcessor` 负责蛋白结构样本标准化处理。

# sampling_strategy

- 训练路径由 `SimpleFoldTrainingDataset` 管理样本索引。
- 推理路径由 `SimpleFoldPredictionDataset` 管理预测样本。
- DataModule 负责构建训练或推理 dataloader。
- 数据划分依赖外部配置或预处理数据清单。

# data_transform

- mmCIF 解析为结构对象。
- 结构对象被 token 化并最终组装为 SimpleFold sample。
- 训练阶段可能需要生成噪声位置、时间步和结构特征。
- 推理阶段重点是把输入结构/序列条件转换为模型可读 batch。

# input_schema

```text
预处理输入:
  mmcif_path 或 pdb_id
  output_dir
  chain/filter 配置: 可选

训练输入:
  processed_data_dir
  dataset split/config

推理输入:
  prediction_input_path
  output_dir
```

# output_schema

```text
SimpleFold sample:
  feats: dict
  coordinates / positions: 结构坐标相关字段
  masks: 有效残基/原子 mask
  metadata: sample id / chain 信息

模型 batch:
  noised_pos: 可选训练字段
  t: 可选时间步字段
  feats: dict
```

# constraints

- SimpleFold 协议不同于 OpenFold feature dict 和 Protenix feature dict。
- 原始 mmCIF 质量、缺失原子和链选择会影响样本生成。
- 训练/推理 DataModule 依赖预处理数据布局。
- 不负责 MSA 搜索、template 检索或 ligand-rich 复合物建模。

# code_references

- `{onescience_path}/onescience/src/onescience/datapipes/simplefold/process_mmcif.py`
- `{onescience_path}/onescience/src/onescience/datapipes/simplefold/process_structure.py`
- `{onescience_path}/onescience/src/onescience/datapipes/simplefold/train_datamodule.py`
- `{onescience_path}/onescience/src/onescience/datapipes/simplefold/test_datamodule.py`
- `{onescience_path}/onescience/src/onescience/datapipes/simplefold/processor/protein_processor.py`
