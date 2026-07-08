# launch

Python API 方式调用，通常接在 VQ decoder 后：

```sh
python -c "from onescience.flax_models.protoken.model.decoder import Protein_Decoder; print(Protein_Decoder.__name__)"
```

# input_schema

准备 single_act、pair_act、seq_mask 和 aatype。single/pair 应来自兼容的 VQ decoder 或 encoder 输出。

# runtime_interfaces

- `Protein_Decoder.__call__`: 执行 frame 初始化、结构模块坐标恢复和 pLDDT 预测。

# main_functions

- `__call__`

# execution_resources

结构模块计算较重；资源消耗与 residue 数、结构迭代层数和 pair 表征大小相关。

# operation_limits

源码中存在将 aatype 置为 Gly 的处理，迁移到真实残基生成时需特别核对。该模块不负责 latent 采样。
