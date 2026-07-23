# launch

该原语描述 OneScience AlphaFold JAX 模型内部的 Haiku 组件。组件应在 `hk.transform` 作用域内构造，并由完整 `RunModel` 或 `AlphaFold` 模型提供配置、参数树和 feature batch；不要把内部模块当作独立文件入口。

```sh
python -c "from onescience.flax_models.alphafold.model.modules import AlphaFoldIteration, EmbeddingsAndEvoformer, EvoformerIteration; from onescience.flax_models.alphafold.model.folding import StructureModule; import inspect; print(inspect.signature(AlphaFoldIteration)); print(inspect.signature(AlphaFoldIteration.__call__)); print(inspect.signature(EmbeddingsAndEvoformer)); print(inspect.signature(EvoformerIteration)); print(inspect.signature(StructureModule))"
```

# input_schema

- `AlphaFoldIteration` 接受 `config`、`global_config`、ensemble/non-ensemble feature 字典和 `is_training`。
- 特征包含 `aatype`、`residue_index`、`seq_mask`、MSA/deletion、模板坐标与 mask；monomer 与 multimer 字段不可混用。
- `StructureModule` 接受 Evoformer `representations`、原始 batch、训练标志和可选 PRNG key。
- 输出包括 MSA/pair/single 表征、结构模块结果和启用的辅助头；训练模式还包含各头损失。

# runtime_interfaces

- `modules.AlphaFoldIteration` / `modules_multimer.AlphaFoldIteration`：单次 recycling 内的完整组件图。
- `EmbeddingsAndEvoformer`：输入嵌入、模板、extra-MSA 和 Evoformer 主干。
- `EvoformerIteration`：单个 Evoformer block。
- `folding.StructureModule` / `folding_multimer.StructureModule`：表征到原子坐标与 frame 的结构头。
- `RunModel.process_features`、`RunModel.predict`：建议用于完整模型集成。

# main_functions

- `AlphaFoldIteration.__call__`
- `EmbeddingsAndEvoformer.__call__`
- `EvoformerIteration.__call__`
- `StructureModule.__call__`

# execution_resources

- 依赖 JAX、Haiku、AlphaFold 参数树和完整特征化数据。
- 长序列、MSA 深度、模板数、recycling 和 ensemble 数决定加速器内存。
- 组件参数名和作用域必须与 checkpoint 的 Haiku 参数树保持一致。

# operation_limits

- 这些是完整模型的内部模块，不提供 FASTA/MSA 搜索、参数加载或结构文件写出。
- monomer 与 multimer 使用不同模块和特征契约。
- 绕过 `RunModel` 时调用方必须自行维护 Haiku RNG、参数树、ensemble 与 recycling 状态。
