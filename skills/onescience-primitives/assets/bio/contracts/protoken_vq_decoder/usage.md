# launch

Python API 方式调用，通常用于解码 VQ latent 的第一阶段：

```sh
python -c "from onescience.flax_models.protoken.model.decoder import VQ_Decoder; print(VQ_Decoder.__name__)"
```

# input_schema

准备 `vq_act`、`seq_mask` 和 `residue_index`；`vq_act` 应来自兼容的 ProToken bottleneck 或 checkpoint latent。

# runtime_interfaces

- `VQ_Decoder.__call__`: 从 VQ latent 恢复 single/pair 表征并输出 distogram。

# main_functions

- `__call__`

# execution_resources

pair 表征和 distogram 输出对 residue 长度平方敏感；长蛋白需关注显存。

# operation_limits

不会输出最终原子坐标；latent channel 或 residue_index 不匹配会导致重建失败或 distogram 偏移。
