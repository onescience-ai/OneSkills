# Model Card: SE3Transformer

## 基本信息

- 模型名：`SE3Transformer`
- 任务类型：`SE(3)-equivariant graph backbone / RFdiffusion internal component`
- 当前状态：`component_only`
- 主实现文件：`./onescience/src/onescience/models/se3_transformer/transformer.py`

## 模型定位

SE3Transformer 是 OneScience 中的 SE(3) 等变图神经网络组件，主要作为 RFdiffusion / RoseTTAFold 结构轨道中的等变更新模块使用。它不是独立的生信任务模型。

补充说明：

- 该目录位于 `onescience.models` 下，但没有对应 `examples/biosciences/se3_transformer` 独立任务入口
- RFdiffusion 通过 `SE3TransformerWrapper` 使用它
- 若用户要改 RFdiffusion 的结构轨道或等变层，可读本卡；若只是跑骨架生成，优先看 `rfdiffusion.md`

## 输入定义

- `SE3Transformer.forward` 输入：
  - `graph: DGLGraph`
  - `node_feats: Dict[str, Tensor]`
  - `edge_feats: Optional[Dict[str, Tensor]]`
  - `basis: Optional[Dict[str, Tensor]]`
- `node_feats` 使用 fiber degree 字符串作为 key：
  - `"0"`: invariant scalar features
  - `"1"`: equivariant vector features
  - 更高 degree 依赖配置
- graph 需要：
  - `graph.edata["rel_pos"]`
- RFdiffusion wrapper 输入：
  - `type_0_features`
  - optional `type_1_features`
  - `edge_features`

## 输出定义

- 若 `return_type` 非空：
  - 返回对应 degree 的特征 tensor
- 若设置 pooling：
  - 返回图级 pooled features
- 否则：
  - 返回 `Dict[str, Tensor]`，key 为 fiber degree
- RFdiffusion wrapper 中：
  - 返回 SE3 更新后的 scalar / vector features dict

## 主干结构

- `Fiber`
  - 描述不同 degree 的通道数
- `get_basis / update_basis_with_fused`
  - 基于相对坐标构造 spherical harmonics / Clebsch-Gordon basis
- `AttentionBlockSE3`
  - SE(3)-equivariant sparse graph attention
- `ConvSE3`
  - tensor field convolution / self interaction
- `NormSE3`
  - degree-aware normalization
- `GPooling`
  - optional graph pooling
- `SE3TransformerWrapper`
  - RFdiffusion 侧的参数初始化与输入包装

## 主要依赖组件

- `SE3Transformer`
- `SE3TransformerPooled`
- `Fiber`
- `AttentionBlockSE3`
- `ConvSE3`
- `NormSE3`
- `GPooling`
- `SE3TransformerWrapper`

## 主要 Shape 变化

- fiber feature tensor 约定：
  - degree `d` feature: `(N_node, C, 2d + 1)`
- edge scalar feature 会追加 `rel_pos.norm()`：
  - `edge_feats["0"]` 增加距离通道
- attention head 内部把 fiber features reshape 到 `(N, num_heads, -1)`

## 默认关键参数

- `num_layers`
- `fiber_in`
- `fiber_hidden`
- `fiber_out`
- `fiber_edge`
- `num_heads`
- `channels_div`
- `tensor_cores`
- `low_memory`
- RFdiffusion wrapper 默认：
  - `num_layers=2`
  - `num_channels=32`
  - `num_degrees=3`
  - `n_heads=4`
  - `div=4`

## 常见修改点

- 改 RFdiffusion SE3 容量：优先改 wrapper 中 `num_layers/num_channels/num_degrees/n_heads`
- 改输入向量通道：同步改 `l1_in_features` 与传入的 `type_1_features`
- 低显存优化：检查 `tensor_cores` 与 `low_memory` 的组合
- 自定义图任务：必须构造 DGL graph、`rel_pos`、fiber-compatible feature dict

## 风险点

- 它不是完整蛋白结构预测模型，不能替代 OpenFold / Protenix / AlphaFold3
- feature dict 的 degree 维度必须满足 `(N, C, 2d+1)`，普通 `(N, C)` 张量不能直接喂入 degree `1+`
- DGL graph 的 `rel_pos` 缺失会导致 basis 构造失败
- RFdiffusion wrapper 会特殊初始化最后 self-interaction 层，修改初始化会影响采样稳定性

## 推荐检索顺序

1. 如果任务是 RFdiffusion 推理，先看 `rfdiffusion.md`
2. 如果任务是改等变结构轨道，再看本模型卡
3. 再读 `se3_transformercomponents.md`
4. 最后读 `transformer.py`、`layers/attention.py`、`basis.py`

## 组件契约入口

- `../contracts/se3transformercomponents.md`

## 源码锚点

- `./onescience/src/onescience/models/se3_transformer/transformer.py`
- `./onescience/src/onescience/models/se3_transformer/fiber.py`
- `./onescience/src/onescience/models/se3_transformer/basis.py`
- `./onescience/src/onescience/models/se3_transformer/layers/attention.py`
- `./onescience/src/onescience/models/se3_transformer/layers/convolution.py`
- `./onescience/src/onescience/models/rfdiffusion/SE3_network.py`
