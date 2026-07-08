# component_info

`se3_transformer_components` 是 SE3Transformer 组件契约，覆盖 `SE3Transformer`、`Fiber`、`AttentionBlockSE3`、`ConvSE3` 和 `SE3TransformerWrapper`。原始 contract 中模块族为 `equivariant`，目标统一入口为 `OneEquivariant`，注册名为 `style="SE3Transformer"`，注册状态为 `contract_only`。

# purpose

用于在 DGL 图上执行 SE(3)-equivariant sparse graph attention 和 tensor field convolution，主要服务于 RFdiffusion 的 structure track 等变更新。普通 RFdiffusion 推理通常不需要直接修改该组件。

# input_schema

```text
SE3Transformer.forward:
  graph: DGLGraph
  node_feats: Dict[str, Tensor]
  edge_feats: Optional[Dict[str, Tensor]]
  basis: Optional[Dict[str, Tensor]]

graph 约束:
  graph.edata["rel_pos"] 必须存在

feature 约束:
  degree d feature: (N_node, channels, 2d + 1)
  edge scalar features: edge_feats["0"]

RFdiffusion wrapper:
  G
  type_0_features
  optional type_1_features
  edge_features
```

# output_schema

```text
return_type is None:
  Dict[str, Tensor]

return_type 指定:
  degree tensor

pooling 指定:
  graph-level pooled tensor

RFdiffusion wrapper:
  fiber dict for structure track
```

# parameters

- `SE3Transformer`: `num_layers`、`fiber_in`、`fiber_hidden`、`fiber_out`、`fiber_edge`、`num_heads`、`channels_div`、`return_type`、`pooling`、`norm`、`use_layer_norm`、`tensor_cores`、`low_memory`。
- `SE3TransformerWrapper`: `num_layers=2`、`num_channels=32`、`num_degrees=3`、`n_heads=4`、`div=4`、`l0_in_features=32`、`l0_out_features=32`、`l1_in_features=3`、`l1_out_features=2`、`num_edge_features=32`。

# key_dependencies

- `transformer.py`
- `fiber.py`
- `basis.py`
- `attention.py`
- `convolution.py`
- `SE3_network.py`

# usage_and_risks

组件根据 `rel_pos` 计算 SE(3) basis，将距离追加到 edge scalar features，并通过多层 `AttentionBlockSE3` 与 `ConvSE3` 更新 fiber features。`contract_only` 来自原始 contract，不表示 `OneEquivariant(style="SE3Transformer")` 当前可直接实例化。普通 `(N, C)` tensor 只能作为 degree 0；degree、通道、head reshape 必须与 fiber 配置一致；DGL graph 缺 `rel_pos` 会失败。

# code_references

- `{onescience_path}/onescience/src/onescience/models/se3_transformer/transformer.py`
- `{onescience_path}/onescience/src/onescience/models/se3_transformer/fiber.py`
- `{onescience_path}/onescience/src/onescience/models/se3_transformer/basis.py`
- `{onescience_path}/onescience/src/onescience/models/se3_transformer/layers/attention.py`
- `{onescience_path}/onescience/src/onescience/models/se3_transformer/layers/convolution.py`
- `{onescience_path}/onescience/src/onescience/models/rfdiffusion/SE3_network.py`
