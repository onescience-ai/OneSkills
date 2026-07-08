# launch

Python API 方式调用，位于 ProToken encoder 和 decoder 之间：

```sh
python -c "from onescience.flax_models.protoken.model.bottleneck import BottleneckModel; print(BottleneckModel.__name__)"
```

# input_schema

准备来自 encoder 的连续 single 表征和 residue mask；配置需包含 codebook、latent 维度和量化策略。

# runtime_interfaces

- `BottleneckModel.__call__`: 执行 latent 投影、量化和辅助统计输出。

# main_functions

- `__call__`

# execution_resources

资源取决于 codebook size、latent dimension 和 residue 数；通常小于 pair-heavy 结构模块。

# operation_limits

codebook 与 checkpoint 不一致会导致 token index 无法解码。该模块不产生结构坐标，需与 decoder 联用。
