# launch

Python API 方式调用，通常在 PT-DiT 表征更新块中使用：

```sh
python -c "from onescience.flax_models.Pt_DiT.module.transformer import NormBlock, Transition, OuterProduct, OuterDifference; print(NormBlock.__name__, Transition.__name__, OuterProduct.__name__, OuterDifference.__name__)"
```

# input_schema

准备 residue single 表征、neighbor single 表征、pair 表征和对应 masks。OuterProduct/OuterDifference 需要 single 的 i/j 两侧输入。

# runtime_interfaces

- `NormBlock.__call__`: 执行 layernorm 或 rmsnorm。
- `Transition.__call__`: 对 pair 表征做 FFN/GLU 更新。
- `OuterProduct.__call__`: 从 single 构造 pair update。
- `OuterDifference.__call__`: 从 single 差分构造 pair update。

# main_functions

- `__call__`

# execution_resources

资源消耗主要来自 pair 表征 `(Residues, Neighbors, Channels)`；dense neighbor 模式更耗内存。

# operation_limits

输入 mask 和 neighbor 维度必须对齐；该模块不包含完整 attention block 和 diffusion denoiser。
