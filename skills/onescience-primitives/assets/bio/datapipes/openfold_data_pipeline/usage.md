# launch

Python API 示例：

```sh
python -c "from onescience.datapipes.openfold.data_pipeline import DataPipeline; from onescience.datapipes.openfold.feature_pipeline import FeaturePipeline; dp=DataPipeline(template_featurizer=None); fp=FeaturePipeline({'data': {'common': {}, 'predict': {}}}); print(type(dp).__name__, type(fp).__name__)"
```

# input_schema

```text
推理:
  fasta_path: 蛋白 FASTA
  msa_output_dir: MSA 结果目录
  template_featurizer: template 特征器或 None
  use_precomputed_msas: bool

训练:
  mmcif_dir: mmCIF 数据目录
  alignment_dir: MSA 数据目录
  data_config: OpenFold 数据配置

多聚体:
  多链 FASTA
  paired/unpaired MSA
```

# runtime_interfaces

- `DataPipeline`: 单体 FASTA 到 OpenFold numpy feature。
- `DataPipelineMultimer`: 多聚体 FASTA 到多链 feature。
- `FeaturePipeline`: numpy feature 到 tensor feature。
- `OpenFoldDataModule`: 训练/验证/测试 dataloader 组织。
- `AlignmentRunner`: 调用 MSA 搜索工具。

# main_functions

- `process_fasta`
- `process_multiseq_fasta`
- `process_features`
- `np_to_tensor_dict`
- `train_dataloader`
- `val_dataloader`
- `test_dataloader`

# execution_resources

- MSA/template 搜索主要消耗 CPU、内存和外部数据库 I/O。
- 训练 DataLoader 会读取结构、MSA 和缓存特征。
- 多聚体 pairing 和 crop 对内存更敏感。
- 需要外部命令行工具时，运行环境必须包含对应可执行文件和数据库。

# operation_limits

- 无数据库或外部工具时，只能处理预计算 MSA/template 或简化特征。
- 不支持 Protenix/AF3 JSON 作为原生输入。
- 多聚体路径需要严格区分 chain feature 和 paired/unpaired MSA。
- 配置缺字段时 feature transform 容易在运行期失败。
