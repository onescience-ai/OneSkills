# architecture_overview

BE_MPNN 的主模型类为 `HeteroGNS`，是 BENO（Boundary-Embedded Neural Operator）任务中的边界条件感知异构图消息传递网络。它服务于椭圆型 PDE 代理建模：输入由 BENO datapipe 生成的 `HeteroData`，其中 `G1` 表示场/区域分支，`G2` 表示边界条件分支，模型通过共享结构但参数独立的双图分支学习域内 forcing、几何距离、边界条件与解场之间的映射。

组件定位概括：该组件不是通用分子或蛋白 MPNN，而是面向 PDE 图样本的边界嵌入图神经算子。其关键特征是将边界点序列编码为全局边界向量，并在每轮节点更新中与邻域聚合消息一起注入，从而把复杂边界形状和边界值纳入解场预测。

# parameter_scale

- 默认潜空间维度：`latent_dim=128`
- 默认消息传递步数：`nmessage_passing_steps=10`
- 示例配置中使用的 MLP 层数：`nmlp_layers=2`
- 示例配置中使用的 MLP 隐藏维度：源码默认 `mlp_hidden_dim=128`
- 默认边界嵌入维度：`boundary_dim=128`
- 默认边界 Transformer 层数：源码默认 `trans_layer=3`
- 默认边界 Transformer 头数：`n_heads=2`
- 默认节点输入维度：示例配置为 `nnode_in_features=10`
- 默认边输入维度：示例配置为 `nedge_in_features=7`
- 默认节点输出维度：示例配置为 `nnode_out_features=1`

参数规模主要随 `latent_dim`、`nmessage_passing_steps`、`nmlp_layers`、`boundary_dim` 和 `trans_layer` 增长；图计算显存还与节点数、边数和 batch size 强相关。

# architecture_structure

```text
HeteroGNS
  Encoder
    G1.node_fn: MLP(nnode_in_features -> latent_dim) + LayerNorm
    G1.edge_fn: MLP(nedge_in_features -> latent_dim) + LayerNorm
    G2.node_fn_inbd: MLP(nnode_in_features -> latent_dim) + LayerNorm
    G2.edge_fn_inbd: MLP(nedge_in_features -> latent_dim) + LayerNorm

  Processor
    gnn_stacks: nmessage_passing_steps 个 InteractionNetwork
      面向 G1 图分支
    gnn_stacks_inbd: nmessage_passing_steps 个 InteractionNetwork
      面向 G2 边界分支

  InteractionNetwork
    message:
      concat(x_i, x_j, edge_features)
      -> edge_fn
      -> updated_edge_features
    boundary_fn:
      boundary: (BoundaryNodes, 3)
      -> Transformer(enc_in=3, d_model=boundary_dim, n_heads=2)
      -> boundary_embedding: (boundary_dim)
    update:
      mean aggregation
      concat(aggregated_message, node_state, repeated_boundary_embedding)
      -> node_fn
      -> residual node update

  Decoder
    G1.node_fn: MLP(latent_dim -> nnode_out_features)
    G2.node_fn_inbd: MLP(latent_dim -> nnode_out_features)
    output = decoded_G1 + decoded_G2
```

# input_schema

输入对象为 PyG 风格异构图样本，运行时以字典式访问：

```text
data["G1"]
  x: (NumNodes, nnode_in_features)
    默认 nnode_in_features=10，通常包含坐标、输入场、平滑场、梯度、边界距离等特征
  edge_index: (2, NumEdges)
    图连接索引
  edge_features: (NumEdges, nedge_in_features)
    默认 nedge_in_features=7，由 MeshGenerator.attributes 生成
  boundary: (BoundaryNodes, 3)
    边界点序列；G1 分支通常保留边界坐标并将边界值清零

data["G2"]
  x: (NumNodes, nnode_in_features)
    默认 nnode_in_features=10，BENO datapipe 中间场特征置零以突出边界条件分支
  edge_index: (2, NumEdgesInBoundaryBranch)
  edge_features: (NumEdgesInBoundaryBranch, nedge_in_features)
  boundary: (BoundaryNodes, 3)
    边界坐标和边界值
```

与示例 datapipe 的默认配套约定：

- `RHS_<file_prefix>_all.npy`：源项/forcing 与 cell_state 来源
- `SOL_<file_prefix>_all.npy`：监督目标来源
- `BC_<file_prefix>_all.npy`：边界条件来源
- 默认网格分辨率：`resolution=32`
- 默认邻域参数：`ns=10`
- 默认边界点数假设来自 datapipe：`128`

# output_schema

```text
u: (NumNodes, nnode_out_features)
  默认 nnode_out_features=1
  表示采样节点处预测的标量 PDE 解场
```

训练示例中 `u` 会与 `data["G1+2"].y` 对齐计算 MSE；评估和推理阶段通常使用 datapipe 提供的 `u_normalizer.decode(...)` 将输出恢复到原始物理尺度。

# shape_transformations

```text
输入图样本
  G1.x: (N, 10)
  G1.edge_features: (E1, 7)
  G1.boundary: (Bnd, 3)
  G2.x: (N, 10)
  G2.edge_features: (E2, 7)
  G2.boundary: (Bnd, 3)

Encoder 双分支编码
  G1.x -> node_fn -> x: (N, 128)
  G1.edge_features -> edge_fn -> edge_features: (E1, 128)
  G2.x -> node_fn_inbd -> x_inbd: (N, 128)
  G2.edge_features -> edge_fn_inbd -> edge_inbd_features: (E2, 128)

Processor / G1 分支
  每个 InteractionNetwork:
    boundary: (Bnd, 3)
      -> unsqueeze: (1, Bnd, 3)
      -> Transformer
      -> boundary_embedding: (1, 128)
      -> repeat: (N, 128)
    message concat:
      x_i: (E1, 128)
      x_j: (E1, 128)
      edge_features: (E1, 128)
      -> (E1, 384)
      -> edge_fn -> (E1, 128)
    node update concat:
      aggregated_message: (N, 128)
      x: (N, 128)
      boundary_embedding: (N, 128)
      -> (N, 384)
      -> node_fn -> (N, 128)
    residual:
      x = x_updated + x_residual
      edge_features = edge_updated + edge_residual

Processor / G2 分支
  与 G1 同构，使用独立 gnn_stacks_inbd 参数

Decoder
  x: (N, 128) -> decoded_G1: (N, 1)
  x_inbd: (N, 128) -> decoded_G2: (N, 1)
  u = decoded_G1 + decoded_G2 -> (N, 1)
```

# key_dependencies

- `torch.nn`：MLP、LayerNorm、激活函数与模块组合
- `torch_geometric.nn.MessagePassing`：消息传递框架与 `propagate/message/update` 调用约定
- `onescience.models.beno.transformer.Transformer`：边界点序列编码器
- `BENODatapipe`：生成模型所需的 `G1/G2/G1+2` 异构图样本
- `LpLoss` 与 normalizer：训练/评估阶段的误差计算与尺度恢复

# common_modification_points

- 输入特征维度：当 datapipe 修改 `G1.x/G2.x` 的字段拼接方式时，同步修改 `nnode_in_features`。
- 边特征维度：当 `MeshGenerator.attributes(...)` 输出字段变化时，同步修改 `nedge_in_features`。
- 边界编码方式：可在 `InteractionNetwork.boundary_fn` 中替换或扩展 Transformer，例如加入边界类型 embedding、位置归一化或更强的序列池化。
- 消息传递深度：通过 `nmessage_passing_steps` 调整长程传播能力和计算成本。
- MLP 宽度与深度：通过 `mlp_hidden_dim`、`nmlp_layers` 调整表达能力。
- 分支融合方式：当前 Decoder 使用 `decoded_G1 + decoded_G2`，可改为 concat 后 MLP、门控融合或注意力融合，以增强场分支与边界分支交互。
- 残差策略：当前节点和边都使用简单残差相加，若训练不稳定可加入 dropout、残差缩放或 pre-normalization。

# implementation_risks

- `boundary_fn` 固定以 `enc_in=3` 构造，边界张量最后一维必须为 3，否则会在卷积 token embedding 处报 shape 错误。
- `boundary.repeat(x.shape[0], 1)` 假定每个图样本的边界编码已经池化为 `(1, boundary_dim)`；批量图合并后若多个样本边界被拼成非预期结构，边界向量可能无法逐图对应。
- `trans_layer` 在配置注释中可能被误写为“消息传递层数”，但源码中它实际控制边界 Transformer encoder 层数；消息传递步数由 `nmessage_passing_steps` 控制，示例实例化未显式传入时使用默认 10。
- Processor 中 G1/G2 两套 `InteractionNetwork` 参数互不共享，修改一侧结构时应同步考虑另一侧。
- Decoder 直接相加两个分支输出，要求 `G1` 和 `G2` 的节点顺序与节点数一致。
- BENO datapipe 对边界点数、网格分辨率、RHS/SOL/BC 列语义存在默认假设，模型本身不做输入校验。
- 源码中 `from .transformer import *` 与未使用的 `pdb` 会增加命名污染和维护噪声。

# code_references

- `{onescience_path}/onescience/src/onescience/models/beno/BE_MPNN.py`
