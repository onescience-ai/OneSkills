# launch

Python API 方式调用，通常作为 latent denoiser 使用：

```sh
python -c "from onescience.flax_models.MolSculptor.src.model.diffusion_transformer import DiffusionTransformer; print(DiffusionTransformer.__name__)"
```

# input_schema

准备 latent tokens、tokens_mask、time、可选 label 和 rope index；time 必须与 diffusion scheduler 的 timestep 定义一致。

# runtime_interfaces

- `DiffusionTransformer.__call__`: 执行条件去噪预测。
- `TimestepEmbedder.__call__`: 生成时间嵌入。
- `LabelEmbedder.__call__`: 生成标签条件嵌入。
- `DiffusionTransformerBlock.__call__`: 单个 DiT block。

# main_functions

- `__call__`
- `timestep_embedding`
- `token_drop`

# execution_resources

需要加速设备更合适；资源消耗随 token 数、hidden size、迭代层数和 batch size 增长。

# operation_limits

该模块没有采样循环和化学后处理；预测目标必须与训练配置一致。用于蛋白-配体任务时需要额外条件注入适配。
