# launch

Python API 示例：

```sh
python -c "from onescience.datapipes.protenix.infer_data_pipeline import InferenceDataset, get_inference_dataloader; ds=InferenceDataset(input_json_path='/path/to/protenix_input.json', dump_dir='/tmp/protenix_features'); loader=get_inference_dataloader(ds, batch_size=1, num_workers=0); print(type(loader).__name__)"
```

# input_schema

```text
推理:
  input_json_path: Protenix/AF3 JSON
  dump_dir: 中间结果目录
  msa_dir: 可选 MSA 目录

训练:
  dataset config: 样本清单、数据根目录、权重、过滤条件
  msa config: protein/RNA MSA 设置
  dataloader config: batch、worker、分布式参数
```

# runtime_interfaces

- `InferenceDataset`: Protenix 推理数据集。
- `get_inference_dataloader`: 构建推理 dataloader。
- `DataPipeline`: 训练/数据集侧处理 pipeline。
- `Featurizer`: 组装模型特征。
- `get_dataloaders`: 构建训练/验证数据加载器。

# main_functions

- `get_inference_dataloader`
- `get_dataloaders`
- `process`
- `__getitem__`
- `tokenize`
- `featurize`

# execution_resources

- JSON/mmCIF/MSA 解析主要消耗 CPU、内存和文件 I/O。
- ligand/CCD 处理需要化学结构依赖。
- 多数据集训练和大 MSA 会增加内存压力。
- 分布式训练需要外部初始化进程组。

# operation_limits

- 不兼容 OpenFold batch 协议。
- 复杂 ligand 或未知 CCD code 可能导致解析失败。
- 完整训练需要样本清单、权重、过滤配置和标签/坐标数据。
- 推理路径不等同于训练采样路径。
