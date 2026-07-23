# launch

AlphaFold3 使用 `src/onescience/flax_models/alphafold3` 中的 Haiku 模型。调用方负责准备模型配置、参数、随机数和已经 featurise 的 `BatchDict`：

```sh
python -c "from onescience.flax_models.alphafold3.model.model import Model; import inspect; print(inspect.signature(Model)); print(inspect.signature(Model.__call__)); print(inspect.signature(Model.get_inference_result))"
```

# input_schema

- `model_config`：`Model.Config`，主要字段包括 `num_recycles`、`return_embeddings`、`return_distogram`、Evoformer 与 diffusion/confidence/distogram head 配置。
- `model_params`：与配置和化学常量版本匹配的 Haiku 参数树。
- `feature_batch`：AF3 featurisation 产生的 `BatchDict`，描述 protein、RNA、DNA、ligand、ion、bond、MSA、template 和 atom/token 映射。
- `rng_key`：JAX PRNG key，控制扩散采样。
- `Model.__call__` 返回 diffusion samples、confidence 输出和 distogram；按配置可附带 single/pair embeddings。
- `get_inference_result` 将张量结果转换为结构、标量置信度和可写出数组。

# runtime_interfaces

- `DataPipeline.process`：补齐序列搜索、template 和化学输入信息。
- `featurisation.featurise_input`：把 fold input 转成模型 `BatchDict`。
- `Model(config)`：构建完整 AF3 网络。
- `Model.__call__(batch, key=None)`：执行 recycle、diffusion 和 heads。
- `Model.get_inference_result(batch, result, target_name)`：生成每个扩散样本的结构化推理结果。

# main_functions

- `process`
- `featurise_input`
- `__call__`
- `get_inference_result`
- `get_predicted_structure`

# execution_resources

- 需要 JAX/Haiku、AF3 参数、CCD 数据文件和与输入分子类型匹配的 featurisation 依赖。
- 从序列构建 MSA/template 时需要数据库与搜索工具；预计算 features 可跳过该阶段。
- token-pair 表征为平方复杂度，长链和大型复合物需要 GPU/TPU、大显存及受控 diffusion sample 数。

# operation_limits

- 不能把 Protenix 或 OpenFold 的 feature dict 直接传给 AF3 `Model`。
- 配体、自定义 CCD、共价键和 atom/token 映射必须在 featurisation 阶段一致。
- 模型类不负责参数发现、输入 JSON 解析或结果落盘；后续技能应围绕这些 API 构建 adapter。
- 权重与模型配置、化学常量版本不一致会导致 shape 或语义错误。
