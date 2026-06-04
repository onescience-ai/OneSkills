# Contract: SE3TransformerComponents

## 基本信息

- 组件名：`SE3Transformer / Fiber / AttentionBlockSE3 / ConvSE3 / SE3TransformerWrapper`
- 所属模块族：`equivariant`
- 统一入口：`OneEquivariant`
- 注册名：`style="SE3Transformer"`
- 注册状态：`contract_only`

## 组件职责

SE3Transformer 组件负责在 DGL 图上执行 SE(3)-equivariant sparse graph attention 和 tensor field convolution，主要服务于 RFdiffusion 的结构轨道等变更新。

补充说明：

- 契约层统一收束到 `OneEquivariant`，源码当前仍由 `RFdiffusion` 通过 `SE3TransformerWrapper` 直接实例化
- 它是 RFdiffusion 内部等变 backbone，不是完整结构预测或设计模型
- 若任务是普通 RFdiffusion 推理，默认不需要直接改本组件

## 支持输入

- 2D 输入：`not_applicable`
- 3D 输入：`equivariant_graph`
- `SE3Transformer.forward`：
  - `graph: DGLGraph`
  - `node_feats: Dict[str, Tensor]`
  - `edge_feats: Optional[Dict[str, Tensor]]`
  - `basis: Optional[Dict[str, Tensor]]`
- graph 约束：
  - `graph.edata["rel_pos"]` 必须存在
- feature 约束：
  - degree `d` feature shape: `(N_node, channels, 2d + 1)`
  - edge scalar features 通常放在 `edge_feats["0"]`
- RFdiffusion wrapper：
  - `G`
  - `type_0_features`
  - optional `type_1_features`
  - `edge_features`

内部统一做法：

- 根据 `rel_pos` 计算 SE(3) basis
- 将距离 `r = ||rel_pos||` 追加到 edge scalar features
- 多层 `AttentionBlockSE3` 更新 fiber features
- 可选 `NormSE3`
- 最后一层 `ConvSE3` 输出目标 fiber
- RFdiffusion wrapper 特殊处理 fiber_in / fiber_hidden / fiber_out，并重置参数初始化

## 构造参数

- `SE3Transformer`
  - `num_layers`
  - `fiber_in`
  - `fiber_hidden`
  - `fiber_out`
  - `fiber_edge`
  - `num_heads`
  - `channels_div`
  - `return_type`
  - `pooling`
  - `norm`
  - `use_layer_norm`
  - `tensor_cores`
  - `low_memory`
- `SE3TransformerWrapper`
  - `num_layers=2`
  - `num_channels=32`
  - `num_degrees=3`
  - `n_heads=4`
  - `div=4`
  - `l0_in_features=32`
  - `l0_out_features=32`
  - `l1_in_features=3`
  - `l1_out_features=2`
  - `num_edge_features=32`

## 输出约定

- `return_type is None`：
  - 返回 `Dict[str, Tensor]`
- `return_type` 指定：
  - 返回对应 degree tensor
- `pooling` 指定：
  - 返回图级 pooled tensor
- RFdiffusion wrapper：
  - 返回 SE3 更新后的 fiber dict，供 structure track 继续使用

如果有明确边界条件，也写在这里：

- `low_memory=True` 只有配合 tensor cores 路线才有实际意义
- `fiber_in/fiber_hidden/fiber_out` 的 degree 和通道必须与输入特征匹配
- `num_heads` 与 key/value fiber 通道 reshape 需要兼容
- RFdiffusion wrapper 中最后 self-interaction 层被零初始化，不要轻易改变

## 典型调用位置

- `onescience.models.rfdiffusion.SE3_network.SE3TransformerWrapper`
- `RFdiffusion` 的 `IterativeSimulator` / structure track 内部
- 自定义 SE(3) 等变图任务

## 典型参数

- RFdiffusion 常见 wrapper：
  - `num_layers=2`
  - `num_channels=32`
  - `num_degrees=3`
  - `n_heads=4`
  - `div=4`
- 契约层目标调用：
  - `OneEquivariant(style="SE3Transformer", ...)`

## 风险点

- `style="SE3Transformer"` 是 skill 契约归一名，不表示当前源码已经在 `OneEquivariant` registry 中可直接实例化
- 普通 `(N, C)` scalar tensor 只能作为 degree 0；vector / tensor features 需要按 fiber 维度组织
- DGL graph 缺 `rel_pos` 会导致 basis 构造失败
- 该组件不负责 diffusion schedule、contig map 或 PDB 输出，不能替代 RFdiffusion sampler
- 若改通道或 degree，RFdiffusion 后续模块的输入输出也可能需要同步调整

## 源码锚点

- `./onescience/src/onescience/models/se3_transformer/transformer.py`
- `./onescience/src/onescience/models/se3_transformer/fiber.py`
- `./onescience/src/onescience/models/se3_transformer/basis.py`
- `./onescience/src/onescience/models/se3_transformer/layers/attention.py`
- `./onescience/src/onescience/models/se3_transformer/layers/convolution.py`
- `./onescience/src/onescience/models/rfdiffusion/SE3_network.py`
