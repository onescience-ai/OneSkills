# launch

AlphaFold 模型通过 `src/onescience/flax_models/alphafold` 中的 JAX API 使用。数据管线先生成 raw feature dict，`RunModel` 再完成特征处理和推理：

```sh
python -c "from onescience.flax_models.alphafold.model.model import RunModel; import inspect; print(inspect.signature(RunModel)); print(inspect.signature(RunModel.process_features)); print(inspect.signature(RunModel.predict))"
```

# input_schema

- `model_config`：`ml_collections.ConfigDict`，其中 `config.model.global_config.multimer_mode` 决定单体或 multimer 网络。
- `model_params`：与配置匹配的 JAX 参数树；缺省时 `RunModel.init_params` 会随机初始化，只适合结构或接口测试。
- `raw_features`：单体 `DataPipeline` 或 multimer `DataPipelineMultimer` 生成的 NumPy feature dict，包含序列、MSA、template、mask、residue index 等字段。
- `random_seed`：控制特征采样和 multimer MSA sampling。
- `predict` 返回模型结果字典，包含结构模块输出、atom 坐标、pLDDT/PAE/PTM/IPTM 等可用置信度字段；具体字段随 preset 变化。

# runtime_interfaces

- `DataPipeline.process`：从序列及数据库搜索结果构造单体 raw features。
- `DataPipelineMultimer.process`：构造多链特征、MSA pairing 和 chain merge 结果。
- `RunModel(config, params)`：绑定模型配置与权重。
- `RunModel.process_features(raw_features, random_seed)`：把 raw features 转为网络输入。
- `RunModel.eval_shape(feat)`：不执行完整数值推理地检查输出结构。
- `RunModel.predict(feat, random_seed)`：执行 JAX 推理。
- `get_confidence_metrics(prediction_result, multimer_mode)`：从预测结果计算排名与置信度指标。

# main_functions

- `process`
- `process_features`
- `eval_shape`
- `predict`
- `get_confidence_metrics`

# execution_resources

- 需要 JAX、Haiku、模型参数以及与任务匹配的 MSA/template 特征；从原始 FASTA 构建特征时还需要数据库和外部搜索工具。
- GPU/TPU 适合模型推理；数据库搜索主要消耗 CPU、内存和磁盘 I/O。
- 训练或微调代码必须显式提供参数初始化、optimizer、loss 与数据迭代逻辑；`RunModel.predict` 本身是推理封装。

# operation_limits

- AlphaFold v2 主要处理蛋白单体和 multimer，不支持 AF3 式核酸、配体和自定义化学组分输入。
- 单体和 multimer 的 feature dict 不可混用；配置、参数与数据 preset 必须一致。
- 随机初始化只能验证接口，不能产生可信结构。
- MSA、template、数据库版本及 template 截止日期影响结果质量和可复现性。
