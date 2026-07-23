# architecture_overview

AlphaFold 资源的公开入口是 `onescience.flax_models.alphafold.model.model.RunModel`。它用 JAX、Haiku 和 `ml_collections.ConfigDict` 封装单体与多聚体 AlphaFold：`config.model.global_config.multimer_mode` 决定调用 `modules.AlphaFold` 还是 `modules_multimer.AlphaFold`，模型变换后的 `init` 与 `apply` 均由 `jax.jit` 编译。

# parameter_scale

- `RunModel(config, params=None)` 的网络规模完全由传入配置和参数树决定。
- `random_seed` 同时用于参数初始化、特征处理和预测；多聚体模式下还控制 MSA sampling。
- 资源没有独立的训练器或训练超参数入口；`RunModel` 固定以 `is_training=False` 执行。

# architecture_structure

```text
raw feature dict
  -> RunModel.process_features
  -> processed feature dict
  -> Haiku AlphaFold (monomer or multimer)
  -> structure and auxiliary prediction dictionaries
  -> get_confidence_metrics
  -> prediction dictionary with confidence fields
```

单体实现位于 `modules.py`，多聚体实现位于 `modules_multimer.py`；折叠结构模块位于 `folding.py`。

# input_schema

- 构造输入：`config: ml_collections.ConfigDict`，可选 `params: Mapping[str, Mapping[str, jax.Array]]`。
- `process_features(raw_features, random_seed)` 接收数据管线生成的 NumPy feature dict；多聚体模式直接返回输入，单体模式调用 `features.np_example_to_features`。
- `predict(feat, random_seed)` 接收处理后的 feature dict。
- 输入字段及 shape 由所用单体/多聚体配置和 feature pipeline 共同约束，不能用 FASTA 字符串直接替代。

# output_schema

- `process_features` 返回适合模型调用的特征字典。
- `eval_shape` 返回与模型输出树对应的 `jax.ShapeDtypeStruct`。
- `predict` 返回模型结果字典，并加入可计算的 `plddt`、predicted aligned error、`ptm`、多聚体 `iptm` 和 `ranking_confidence`。
- 该 API 返回内存对象，不定义 PDB、JSON 或目录落盘格式。

# shape_transformations

1. 原始特征由单体 feature processor 转为配置所需的批量数组；多聚体特征保持数据管线协议。
2. Haiku `apply` 产生结构、距离和置信度头的数组树。
3. `get_confidence_metrics` 从 logits 派生逐残基或标量置信度，并合并回结果字典。

# key_dependencies

- `alphafold_jax_components`

# common_modification_points

- 切换单体/多聚体时修改配置并同时使用匹配的特征管线和参数树。
- 替换 checkpoint 时保持 Haiku 参数树与配置结构一致。
- 构建更高层推理时，可在 `predict` 返回值之后增加结构序列化，但不要改变 `RunModel` 的 feature dict 契约。
- 如需训练，应单独规划 JAX/Haiku 训练循环；当前公开包装器不提供训练步骤。

# implementation_risks

- 未提供参数时 `init_params` 会随机初始化，这不等价于加载预训练模型。
- 单体处理后的特征不能直接当作多聚体特征复用，反之亦然。
- 配置、参数树和 feature dict 任一不匹配都会在 JIT tracing 或 apply 阶段失败。
- `predict` 会等待所有设备输出就绪，不能把返回前的异步状态当作完成。

# code_references

- `{onescience_path}/onescience/src/onescience/flax_models/alphafold/model/model.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphafold/model/modules.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphafold/model/modules_multimer.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphafold/model/folding.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphafold/model/features.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphafold/data/pipeline.py`
- `{onescience_path}/onescience/src/onescience/flax_models/alphafold/data/pipeline_multimer.py`
