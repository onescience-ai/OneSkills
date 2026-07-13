# launch

```sh
python -c "from onescience.models.se3_transformer import SE3Transformer; print(SE3Transformer.__name__)"
```

# input_schema

准备带 `edata["rel_pos"]` 的 DGL 图、按 degree 组织的 node feature dict、可选 edge feature dict 和 basis。RFdiffusion wrapper 通常提供 `G`、`type_0_features`、可选 `type_1_features` 和 `edge_features`。

# runtime_interfaces

- `SE3Transformer.forward`: 执行等变图 attention 和 convolution。
- `SE3TransformerWrapper.forward`: RFdiffusion 结构轨道中的封装入口。
- `get_basis`: 根据相对位置构造 SE(3) basis。

# main_functions

- `forward`
- `add_argparse_args`

# execution_resources

需要 DGL 图环境和张量场特征组织。图规模、edge 数、degree 数、hidden channel 和 attention head 数会影响显存。

# operation_limits

`contract_only` 表示不可假设 `OneEquivariant(style="SE3Transformer")` 可运行。该组件不负责 diffusion schedule、contig map 或 PDB 输出，不能替代 RFdiffusion sampler。
