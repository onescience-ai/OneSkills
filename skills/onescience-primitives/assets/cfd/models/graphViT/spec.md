# architecture_overview

graphViT 的主模型类为 `GraphViT`，面向 Eagle 数据集中的二维非结构网格流体动力学时序预测。模型的整体设计是“局部图编码 + 簇级池化 + 全局 Transformer + 节点级解码”的层级结构：先在原始 mesh graph 上用 GNN 提取局部物理和几何特征，再把节点聚合到 cluster latent graph，在簇空间用自注意力捕获远距离依赖，最后把簇级全局信息散射回节点并预测下一时刻状态增量。

组件定位概括：该组件是网格流体预测模型，不是图分类模型，也不是规则网格图像 ViT。它的关键特征是把大规模非结构网格压缩为固定数量簇，在簇级别执行全局注意力，从而降低直接对所有节点做注意力的成本，并保留节点级输出能力。

# parameter_scale

源码默认参数：

- `w_size=512`：簇级 latent 特征维度
- `n_attention=4`：簇级 Transformer block 数量
- `nb_gn=4`：Encoder 中 GNN 消息传递层数
- `n_heads=4`：Transformer 注意力头数
- `pos_start=-3`：傅里叶位置编码最低频率指数
- `pos_length=8`：傅里叶频带数
- `noise_std=0.0`：训练时可选初始状态噪声强度

Eagle 示例配置：

- `state_size=4`：状态维度，通常为二维速度加两通道压力/压强相关量
- `w_size=512`
- `n_cluster=40`
- `window_length_train=6`
- `window_length_val=25`
- `window_length_test=25`

参数规模主要由 `w_size`、`n_attention`、`nb_gn`、`state_size` 和 Transformer 的 `n_heads` 决定；运行显存还随 batch size、时间窗口长度、节点数、边数、cluster 数和每簇最大节点数增长。

# architecture_structure

```text
GraphViT
  positional_encoder: OneEmbedding(style="FourierPosEmbedding")
    mesh_pos + clusters + clusters_mask
    -> mesh_posenc: 节点绝对位置 + 相对簇中心位置编码
    -> cluster_posenc: 簇中心位置编码

  encoder: OneEncoder(style="GraphViTEncoder")
    node input: concat(state, node_type)
    edge input: sender_position - receiver_position + distance_norm
    -> node MLP / edge MLP
    -> nb_gn 层 GNN 消息传递
    -> V: 节点隐特征
    -> E: 边隐特征

  graph_pooling: OnePooling(style="RNNClusterPooling")
    V + mesh_posenc + clusters + clusters_mask
    -> 按簇 gather 节点序列
    -> GRU pooling
    -> W: 簇级 latent 特征

  attention: n_attention 个 OneTransformer(style="PreLNTransformerBlock")
    W + cluster_posenc + attention_mask
    -> 簇级全局交互
    -> LayerNorm

  graph_retrieve: OneDecoder(style="GraphViTDecoder")
    W + V + clusters + mesh_posenc + edges + E
    -> 簇特征 scatter 回节点
    -> GNN 融合局部边信息
    -> MLP 输出 next_output

  自回归状态更新
    next_state = previous_state + next_output
    输入/墙面/禁用节点按真实 state 覆盖
```

# input_schema

`GraphViT.forward(...)` 接收普通张量，不接收 PyG 图对象。典型输入由 `EagleDatapipe` 产生：

```text
mesh_pos: (Batch, Time, NumNodes, 3)
  节点坐标，源码主模型按 3 维坐标传给 FourierPosEmbedding。

edges: (Batch, Time, NumEdges, 2)
  边索引，通常由 triangles.npy 转换为双向边。

state: (Batch, Time, NumNodes, state_size)
  节点物理状态；Eagle 示例 state_size=4，由 velocity 和 pressure 拼接得到。

node_type: (Batch, Time, NumNodes, 9)
  节点类型 one-hot；源码中使用索引 0/2/4/5/6 区分 normal、disable、input、output、wall。

clusters: (Batch, Time, NumClusters, MaxClusterSize)
  每个簇包含的节点索引；Eagle 示例 n_cluster=40。

clusters_mask: (Batch, Time, NumClusters, MaxClusterSize)
  簇内有效节点掩码。

apply_noise: bool
  是否对初始状态中 normal/output 节点注入噪声；默认调用可设 False，训练示例设 True。
```

与 EagleDatapipe 的数据存储约定：

- split 文件：`train.txt`、`valid.txt`、`test.txt`
- 每个仿真目录：`sim.npz`、`triangles.npy`
- cluster 文件：`constrained_kmeans_<n_cluster>.npy`
- `sim.npz` 字段来源：`pointcloud`、`VX`、`VY`、`PS`、`PG`、`mask`

# output_schema

```text
velocity_hat: (Batch, Time, NumNodes, state_size)
  自回归滚动后的完整状态序列，包含初始状态和每一步预测状态。

output_hat: (Batch, Time - 1, NumNodes, state_size)
  每个预测步的状态增量，即 next_output。

target: (Batch, Time - 1, NumNodes, state_size)
  训练目标增量，定义为 state[:, t] - previous_predicted_state。
```

训练脚本会将 `velocity_hat[..., :2]` 视为速度预测，将 `velocity_hat[..., 2:]` 视为压力相关预测，并在反归一化后计算速度、压力和增量损失。

# shape_transformations

```text
输入时间窗
  mesh_pos: (B, T, N, 3)
  edges: (B, T, M, 2)
  state: (B, T, N, S)
  node_type: (B, T, N, 9)
  clusters: (B, T, K, Cmax)
  clusters_mask: (B, T, K, Cmax)

自回归循环 t = 1 ... T-1
  当前状态:
    state_hat[-1]: (B, N, S)

  Fourier 位置编码
    mesh_pos[:, t-1] + clusters[:, t-1]
      -> mesh_posenc: (B, N, 3 * 2 * pos_length * 2)
         pos_length=8 时为 (B, N, 96)，包含绝对和相对位置编码
      -> cluster_posenc: (B, K, 3 * 2 * pos_length)
         pos_length=8 时为 (B, K, 48)

  GraphViTEncoder
    concat(state_hat[-1], node_type[:, t-1])
      -> node input: (B, N, S + 9)
      -> node MLP -> (B, N, 128)
    edge geometry:
      sender - receiver: (B, M, 3)
      norm: (B, M, 1)
      -> edge input: (B, M, 4)
      -> edge MLP -> (B, M, 128)
    GNN layers:
      concat(V, mesh_posenc) -> (B, N, 224) when pos_length=8
      -> V: (B, N, 128)
      -> E: (B, M, 128)

  RNNClusterPooling
    gather V and mesh_posenc by clusters
      -> (B, K, Cmax, 128 + 96)
      -> GRU hidden w_size
      -> W: (B, K, 512)

  Attention mask
    clusters_mask.sum(-1) == 0
      -> empty-cluster mask
      -> (B * n_attention, K, K) in GraphViT.forward

  PreLN Transformer blocks
    concat(W, cluster_posenc)
      -> attention embedding: (B, K, 512 + 48)
      -> MultiheadAttention
      -> linear projection
      -> W: (B, K, 512)

  GraphViTDecoder
    scatter W by clusters -> W_nodes: (B, N, 512)
    concat(V, W_nodes, mesh_posenc)
      -> nodes: (B, N, 736)
    GNN + MLP
      -> next_output: (B, N, S)

  状态更新与边界覆盖
    next_state = state_hat[-1] + next_output
    node_type in input/wall/disable
      -> next_state = ground truth state[:, t]
```

# key_dependencies

- `OneEncoder(style="GraphViTEncoder")`：局部节点和边编码
- `OnePooling(style="RNNClusterPooling")`：节点到簇的 RNN 池化
- `OneTransformer(style="PreLNTransformerBlock")`：簇级全局注意力
- `OneDecoder(style="GraphViTDecoder")`：簇到节点检索与状态增量解码
- `OneEmbedding(style="FourierPosEmbedding")`：绝对/相对傅里叶位置编码
- `EagleDatapipe`：Eagle 网格时序数据读取、padding、cluster 和 mask 输出
- `StandardMLP`、`GNNLayer`、`scatter_sum`：底层图消息传递和 MLP 组件

# common_modification_points

- 状态维度：若新增物理量或改变压力/速度通道，修改 `state_size`，并同步修改训练损失中速度/压力通道切分。
- 时间窗长度：通过 Eagle 配置中的 `window_length_train/val/test` 调整滚动预测长度。
- 聚类数量：通过 `n_cluster` 和对应 `constrained_kmeans_<n_cluster>.npy` 控制簇级图规模。
- 全局建模能力：通过 `w_size`、`n_attention`、`n_heads` 调整簇级 Transformer 容量。
- 局部消息传递能力：通过 `nb_gn` 调整 Encoder 层数，必要时扩展 Decoder 的 GNN 深度。
- 位置编码：修改 `pos_start`、`pos_length` 可调整傅里叶频率覆盖范围；若坐标维度变化，需要同步检查编码维度假设。
- 边界覆盖策略：当前 input/wall/disable 节点强制使用真实下一步状态，可按任务需要扩展节点类型或改成软约束损失。
- 噪声注入：当前 `noise_std=0.0`，若做鲁棒训练可设为非零并仅对 normal/output 节点生效。

# implementation_risks

- `GraphViTEncoder` 的独立模块版本对 edge MLP 输入维度写为 3，但源码主路径配合 3D 坐标时边特征是 `distance(3)+norm(1)=4`；如果工厂加载的组件未与主模型坐标维度一致，可能出现 shape 错误。
- `PreLNTransformerBlock` 要求 `w_size + 4 * pos_length` 能被 `n_heads` 整除；默认 `512 + 32 = 544` 可被 4 整除。
- `GraphViT.forward` 构造 attention mask 时使用 `len(self.attention)` 作为 repeat 维度，而底层 MultiheadAttention 通常按 `B * n_heads` 接收 mask；当 `n_attention != n_heads` 时存在潜在不一致风险，默认二者均为 4。
- `next_state[mask, :] = state[:, t][mask, :]` 使用布尔索引覆盖边界节点，对 batch/time/node 维度广播非常敏感。
- `clusters` 中索引必须在节点 padding 范围内；空簇和 padding 节点依赖 `clusters_mask` 正确处理。
- 模型是自回归滚动，长时间预测会累积误差；训练窗口和评估窗口差异过大时需要关注稳定性。
- EagleDatapipe 出错样本可能返回空字典，训练脚本会跳过空 batch，但坏样本过多会影响有效训练。

# code_references

- `{onescience_path}/onescience/src/onescience/models/graphvit/graphViT.py`
