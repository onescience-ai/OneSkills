# launch

MolSculptor 在 OneScience 中是 Flax 分子扩散 Transformer。代码生成应直接使用 `DiffusionTransformer` 的 `init/apply` 接口；完整分子编码—去噪—解码流程可使用同包的 `Inferencer`。

```sh
python -c "from onescience.flax_models.MolSculptor.src.model.diffusion_transformer import DiffusionTransformer; from onescience.flax_models.MolSculptor.train.inference import InferEncoder, InferDecoder, Inferencer; import inspect; print(inspect.signature(DiffusionTransformer)); print(inspect.signature(DiffusionTransformer.__call__)); print(inspect.signature(InferEncoder)); print(inspect.signature(InferDecoder)); print(inspect.signature(Inferencer))"
```

# input_schema

- `tokens`：浮点分子 token/特征，形状 `[batch, token_count, channels]`。
- `tokens_mask`：有效 token mask，形状 `[batch, token_count]`。
- `time`：扩散时间，形状 `[batch]`；`tokens_rope_index` 为整型旋转位置索引。
- 可选 `label` 和 `force_drop_ids` 用于带标签条件及 classifier-free guidance。
- 主要配置为 `hidden_size`、`n_iterations`、时间/标签嵌入、DiT block、输出头及 `bf16_flag`。
- 输出与输入 token 保持 batch、token 和原始通道维，表示当前扩散步的预测。

# runtime_interfaces

- `DiffusionTransformer(config, global_config)`：完整 Flax 去噪网络。
- `DiffusionTransformer.init(...)`：从样例输入初始化参数树。
- `DiffusionTransformer.apply(...)`：训练和推理共用前向接口。
- `InferEncoder`、`InferDecoder`：分子图与扩散 token 之间的编码/解码组件。
- `Inferencer`：组合 checkpoint、编码器、扩散采样器和解码器的高层推理对象。

# main_functions

- `DiffusionTransformer.__call__`
- `DiffusionTransformer.init`
- `DiffusionTransformer.apply`
- `Inferencer`
- `InferEncoder`
- `InferDecoder`

# execution_resources

- 依赖 JAX、Flax、`ml_collections.ConfigDict` 及和模型配置一致的参数树。
- 训练通常需要加速器；`bf16_flag`、设备 mesh 和 batch 大小应由运行环境决定。
- 完整分子生成还需要匹配的图编码器/解码器、归一化统计量和扩散调度配置。

# operation_limits

- `DiffusionTransformer` 只执行 token 去噪，不单独负责原始分子文件读取、图构建或化学有效性修复。
- `tokens_rope_index` 的类型和拓扑顺序必须与编码器一致。
- 参数树与配置的隐藏维度、block 数、条件嵌入设置不匹配时无法加载。
- 生成分子仍需价态、连通性、去重和任务属性验证。
