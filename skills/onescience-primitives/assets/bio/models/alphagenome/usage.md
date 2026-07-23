# launch

AlphaGenome 推荐通过本地 checkpoint 构造 SDK 模型，再调用序列、区间或变异接口：

```sh
python -c "from onescience.flax_models.alphagenome.model.dna_model import AlphaGenomeModel, create, create_model; import inspect; print(inspect.signature(create)); print(inspect.signature(create_model)); print(inspect.signature(AlphaGenomeModel.predict_sequence)); print(inspect.signature(AlphaGenomeModel.predict_interval)); print(inspect.signature(AlphaGenomeModel.predict_variant))"
```

# input_schema

- `checkpoint_path`：本地 Orbax checkpoint；模型版本必须与 metadata 匹配。
- `organism_settings`：每个 organism 的 FASTA、metadata、GTF、PAS 与 splice-site 注释配置。
- `predict_sequence` 输入 DNA 字符串；模型内部转换为 `(1, sequence_length, 4)` one-hot。
- `predict_interval` 输入 0-based genomic `Interval`，并要求对应 organism 的 FASTA extractor。
- `predict_variant` 输入 interval 与 `Variant`，reference allele 必须和 FASTA 一致。
- 输出为 `dna_output.Output` 或 `VariantOutput`，包含请求的轨迹、contact map、splice/junction 等结构化字段和 metadata。

# runtime_interfaces

- `create(checkpoint_path, organism_settings, model_settings, device)`：从本地权重创建 `AlphaGenomeModel`。
- `AlphaGenomeModel.predict_sequence`：直接对 DNA 序列预测。
- `AlphaGenomeModel.predict_interval`：从参考 FASTA 提取区间并预测。
- `AlphaGenomeModel.predict_variant`：生成 reference/alternate 预测。
- `score_interval`、`score_variant`、`score_ism_variants`：将模型输出转换为任务分数。
- `create_model`：提供底层 Haiku init/apply/junction apply 函数，供训练或微调代码复用。

# main_functions

- `create`
- `create_model`
- `predict_sequence`
- `predict_interval`
- `predict_variant`
- `score_interval`
- `score_variant`

# execution_resources

- 需要 JAX、Haiku、Orbax checkpoint、参考 FASTA/索引及所请求任务的 metadata。
- 约 1 Mbp 输入和多 fold 推理需要较高显存、内存及 checkpoint 读取带宽。
- 训练/微调应复用 `create_model` 与 finetuning 模块，并显式提供数据 iterator、loss、optimizer 和保存策略。

# operation_limits

- 仅用于 DNA/基因组轨迹与变异任务，不用于蛋白结构或分子建模。
- organism、参考基因组、坐标约定、metadata 和 checkpoint 不可混用。
- 未配置 FASTA extractor 时只能使用 `predict_sequence`，不能使用 interval/variant API。
- 默认设备选择偏向 GPU/TPU；CPU 必须显式传入并承担较低性能。
