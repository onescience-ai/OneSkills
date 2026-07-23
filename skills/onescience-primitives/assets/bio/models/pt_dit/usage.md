# launch

PT-DiT 在 OneScience 中是 Flax 的蛋白 token 扩散 Transformer。它是完整去噪模型而非执行脚本；训练和推理均通过 Flax `init/apply`，差别在于扩散时间、条件丢弃和参数更新方式。

```sh
python -c "from onescience.flax_models.Pt_DiT.model.diffusion_transformer import DiffusionTransformer; import inspect; print(inspect.signature(DiffusionTransformer)); print(inspect.signature(DiffusionTransformer.__call__)); print(inspect.signature(DiffusionTransformer.init)); print(inspect.signature(DiffusionTransformer.apply))"
```

# input_schema

- `tokens`：蛋白连续 token/特征，形状 `[batch, token_count, channels]`。
- `tokens_mask`：有效 token mask，形状 `[batch, token_count]`；`time` 为 `[batch]` 扩散时间。
- `tokens_rope_index`：`[batch, token_count]` 的整型位置索引。
- 可选 `label` 和 `force_drop_ids` 控制条件生成与 classifier-free guidance。
- 主要配置为 `hidden_size`、`n_iterations`、时间/标签嵌入、DiT block、输出头、`bf16_flag`。
- 输出形状与输入 `tokens` 相同，表示当前时间步的 token 预测。

# runtime_interfaces

- `DiffusionTransformer(config, global_config)`：完整 Flax 去噪模型。
- `DiffusionTransformer.init(...)`：初始化参数树。
- `DiffusionTransformer.apply(...)`：训练/推理前向。
- `TimestepEmbedder`、`LabelEmbedder`：时间与条件嵌入。
- `DiffusionTransformerBlock`、`DiffusionTransformerOutput`：内部 block 和输出头。

# main_functions

- `DiffusionTransformer.__call__`
- `DiffusionTransformer.init`
- `DiffusionTransformer.apply`

# execution_resources

- 依赖 JAX、Flax 和 `ml_collections.ConfigDict`；参数树必须与配置完全对应。
- 训练通常使用加速器和 JAX mesh；精度、分片和 batch 由上层训练器配置。
- 完整生成还需要 token 编解码器、扩散调度器和 checkpoint 管理。

# operation_limits

- 模型只执行蛋白 token 去噪，不直接读取 FASTA/PDB，也不单独输出最终结构文件。
- mask、RoPE 索引与 token 顺序不一致会破坏注意力和位置编码。
- 条件嵌入启用时必须提供与配置词表一致的 `label`。
- 输出需要由对应解码器和结构质量检查转换、验证。
