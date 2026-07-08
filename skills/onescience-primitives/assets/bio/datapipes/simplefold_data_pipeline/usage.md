# launch

Python API 示例：

```sh
python -c "from onescience.datapipes.simplefold.process_structure import load_input, tokenize_structure, finalize; sample=load_input('/path/to/input_structure.cif'); tokenized=tokenize_structure(sample); final=finalize(tokenized); print(type(final).__name__)"
```

# input_schema

```text
结构预处理:
  input_structure: mmCIF/PDB 或已处理结构文件
  output_dir: 处理结果目录

训练:
  processed_data_dir: 已处理样本目录
  split_config: 训练/验证划分配置

推理:
  prediction_input_path: 预测输入
  batch/runtime config: 推理 batch 配置
```

# runtime_interfaces

- `process_mmcif.process`: 处理 mmCIF 数据。
- `process_structure.load_input`: 加载结构输入。
- `process_structure.tokenize_structure`: 结构 token 化。
- `SimpleFoldTrainingDataModule`: 构建训练数据模块。
- `SimpleFoldInferenceDataModule`: 构建推理数据模块。

# main_functions

- `fetch`
- `parse`
- `process_structure`
- `process`
- `load_input`
- `tokenize_structure`
- `finalize`
- `train_dataloader`
- `val_dataloader`
- `predict_dataloader`

# execution_resources

- 结构解析和预处理主要消耗 CPU、内存和文件 I/O。
- 训练时噪声生成和 batch 组装需要与模型训练环境配合。
- 大规模 mmCIF 预处理建议离线执行并缓存结果。

# operation_limits

- 不生成 OpenFold/Protenix feature dict。
- 不处理 MSA/template 搜索。
- 对缺失严重或非标准结构输入需要先做清洗。
- DataModule 使用前需确认预处理目录布局与配置一致。
