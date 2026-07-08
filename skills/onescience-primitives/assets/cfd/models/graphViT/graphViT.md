# Model Card: graphViT

## 基本信息

- 模型名：`graphViT`
- 任务类型：`cfd / model`
- 当前状态：`public`
- 主实现文件：`{onescience_path}/onescience/src/onescience/models/graphvit/graphViT.py`

## 模型架构概览

graphViT 的主模型类为 `GraphViT`，面向 Eagle 数据集中的二维非结构网格流体动力学时序预测。模型的整体设计是“局部图编码 + 簇级池化 + 全局 Transformer + 节点级解码”的层级结构：先在原始 mesh graph 上用 GNN 提取局部物理和几何特征，再把节点聚合到 cluster latent graph，在簇空间用自注意力捕获远距离依赖，最后把簇级全局信息散射回节点并预测下一时刻状态增量。

组件定位概括：该组件是网格流体预测模型，不是图分类模型，也不是规则网格图像 ViT。它的关键特征是把大规模非结构网格压缩为固定数量簇，在簇级别执行全局注意力，从而降低直接对所有节点做注意力的成本，并保留节点级输出能力。

## 参数规模

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

## 架构结构

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

## 输入模式

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

## 输出模式

```text
velocity_hat: (Batch, Time, NumNodes, state_size)
  自回归滚动后的完整状态序列，包含初始状态和每一步预测状态。

output_hat: (Batch, Time - 1, NumNodes, state_size)
  每个预测步的状态增量，即 next_output。

target: (Batch, Time - 1, NumNodes, state_size)
  训练目标增量，定义为 state[:, t] - previous_predicted_state。
```

训练脚本会将 `velocity_hat[..., :2]` 视为速度预测，将 `velocity_hat[..., 2:]` 视为压力相关预测，并在反归一化后计算速度、压力和增量损失。

## 形状变换

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

## 常见修改点

- 状态维度：若新增物理量或改变压力/速度通道，修改 `state_size`，并同步修改训练损失中速度/压力通道切分。
- 时间窗长度：通过 Eagle 配置中的 `window_length_train/val/test` 调整滚动预测长度。
- 聚类数量：通过 `n_cluster` 和对应 `constrained_kmeans_<n_cluster>.npy` 控制簇级图规模。
- 全局建模能力：通过 `w_size`、`n_attention`、`n_heads` 调整簇级 Transformer 容量。
- 局部消息传递能力：通过 `nb_gn` 调整 Encoder 层数，必要时扩展 Decoder 的 GNN 深度。
- 位置编码：修改 `pos_start`、`pos_length` 可调整傅里叶频率覆盖范围；若坐标维度变化，需要同步检查编码维度假设。
- 边界覆盖策略：当前 input/wall/disable 节点强制使用真实下一步状态，可按任务需要扩展节点类型或改成软约束损失。
- 噪声注入：当前 `noise_std=0.0`，若做鲁棒训练可设为非零并仅对 normal/output 节点生效。

## 实现风险

- `GraphViTEncoder` 的独立模块版本对 edge MLP 输入维度写为 3，但源码主路径配合 3D 坐标时边特征是 `distance(3)+norm(1)=4`；如果工厂加载的组件未与主模型坐标维度一致，可能出现 shape 错误。
- `PreLNTransformerBlock` 要求 `w_size + 4 * pos_length` 能被 `n_heads` 整除；默认 `512 + 32 = 544` 可被 4 整除。
- `GraphViT.forward` 构造 attention mask 时使用 `len(self.attention)` 作为 repeat 维度，而底层 MultiheadAttention 通常按 `B * n_heads` 接收 mask；当 `n_attention != n_heads` 时存在潜在不一致风险，默认二者均为 4。
- `next_state[mask, :] = state[:, t][mask, :]` 使用布尔索引覆盖边界节点，对 batch/time/node 维度广播非常敏感。
- `clusters` 中索引必须在节点 padding 范围内；空簇和 padding 节点依赖 `clusters_mask` 正确处理。
- 模型是自回归滚动，长时间预测会累积误差；训练窗口和评估窗口差异过大时需要关注稳定性。
- EagleDatapipe 出错样本可能返回空字典，训练脚本会跳过空 batch，但坏样本过多会影响有效训练。

## 启动方式

graphViT 通常通过 EagleMeshTransformer 示例脚本运行，配置文件为 `conf/graphvit_eagle.yaml`。

单卡训练示例：

```sh
cd {onescience_path}/onescience/examples/cfd/EagleMeshTransformer
python train_graphvit.py
```

多卡训练示例：

```sh
cd {onescience_path}/onescience/examples/cfd/EagleMeshTransformer
torchrun --standalone --nnodes=1 --nproc_per_node=4 train_graphvit.py
```

评估与动画生成示例：

```sh
cd {onescience_path}/onescience/examples/cfd/EagleMeshTransformer
python eval_graphvit.py
```

Python API 最小调用示例：

```python
from onescience.models.graphvit import GraphViT

model = GraphViT(
    state_size=4,
    w_size=512,
    n_attention=4,
    nb_gn=4,
    n_heads=4,
)

velocity_hat, output_hat, target = model(
    mesh_pos,
    edges,
    state,
    node_type,
    clusters,
    clusters_mask,
    apply_noise=False,
)
```

## 输入模式

原始数据准备遵循 EagleDatapipe 约定：

```text
Eagle_dataset/
  Cre/
  Spl/
  Tri/
    <case_path>/
      sim.npz
      triangles.npy
      constrained_kmeans_40.npy

splits/
  train.txt
  valid.txt
  test.txt
```

示例配置默认参数：

- `datapipe.source.data_dir="${ONESCIENCE_DATASETS_DIR}/Eagle/Eagle_dataset"`
- `datapipe.source.cluster_dir="${ONESCIENCE_DATASETS_DIR}/Eagle/Eagle_dataset"`
- `datapipe.source.splits_dir="./splits/"`
- `datapipe.data.window_length_train=6`
- `datapipe.data.window_length_val=25`
- `datapipe.data.window_length_test=25`
- `datapipe.data.n_cluster=40`
- `datapipe.data.normalized=True`
- `datapipe.data.type_as_onehot=True`
- `datapipe.data.with_cells=True`
- `datapipe.dataloader.batch_size=2`
- `datapipe.dataloader.num_workers=4`
- `model.name="GraphViT"`
- `model.w_size=512`
- `model.state_size=4`
- `training.max_epoch=1000`
- `training.lr=1e-4`
- `training.loss_alpha=0.1`
- `training.patience=100`
- `training.checkpoint_dir="./checkpoints/eagle_graphvit/"`
- `training.gpuid=0`
- `training.max_anim_on_infer=5`

运行时 batch 字段映射：

```text
mesh_pos <- x["mesh_pos"]
edges <- x["edges"].long()
velocity <- x["velocity"]
pressure <- x["pressure"]
state <- concat(velocity, pressure, dim=-1)
node_type <- x["node_type"]
mask <- x["mask"]
clusters <- x["cluster"].long()
clusters_mask <- x["cluster_mask"].long()
cells <- x["cells"]，仅评估可视化使用
```

## 运行时接口

- `GraphViT.forward(mesh_pos, edges, state, node_type, clusters, clusters_mask, apply_noise=False)`：自回归滚动预测主接口，返回完整预测状态、预测增量和目标增量。
- `positional_encoder(...)`：生成节点与簇的傅里叶位置编码。
- `encoder(...)`：把节点状态、节点类型和边几何编码为节点/边隐特征。
- `graph_pooling(...)`：按 cluster 聚合节点特征得到簇级表示。
- `attention`：簇级 Pre-LN Transformer block 列表，用于全局依赖建模。
- `graph_retrieve(...)`：把簇级表示融合回节点并输出状态增量。

## 主要函数

- `forward`

## 执行资源

- 设备：支持 CPU/GPU，训练建议使用 GPU；示例脚本通过 `DistributedManager` 选择设备。
- 数据资源：Eagle 数据量较大，需准备 `sim.npz`、`triangles.npy`、split 文件和预计算 cluster 文件。
- 内存/显存：主要受 `Batch`、`Time`、`NumNodes`、`NumEdges`、`NumClusters`、`MaxClusterSize`、`w_size` 和 Transformer block 数影响。
- 分布式：训练脚本支持 DDP，可用 `mpirun`、`torchrun` 或 Slurm 脚本启动。
- checkpoint：默认保存到 `./checkpoints/eagle_graphvit/best_model.pth`。
- 评估输出：默认从 checkpoint 加载最佳模型，并在 `animation_results/` 保存对比动画。

## 运行限制

- `node_type` 必须是 9 维 one-hot，否则源码中节点类型常量索引不可用。
- `state_size` 必须等于 `velocity` 与 `pressure` 拼接后的最后一维；Eagle 示例为 4。
- 需要预计算 cluster 文件；`n_cluster` 必须与文件名和 datapipe 支持范围一致。
- 输入窗口至少包含 2 个时间步，因为模型从 `t=1` 开始预测。
- 长时间滚动存在误差累积，训练窗口 `6` 与评估窗口 `25` 的差异需要通过验证指标监控。
- 若坐标维度不是 3，需要检查 Fourier position embedding、edge geometry 和 GraphViTEncoder 的边输入维度。
- 常见失败模式包括：cluster 索引越界、空 batch、mask 维度不匹配、attention mask 维度不匹配、checkpoint 缺失或 DDP/non-DDP state_dict key 不兼容。

## 规划决策

### 描述

graphViT 的规划决策重点是判断任务是否为非结构网格上的时序 CFD 预测，并确保 EagleDatapipe、cluster 文件、节点类型编码、状态通道和自回归训练目标之间保持一致。模型以 GraphViT 为主：局部 GNN 处理网格近邻关系，RNNClusterPooling 汇聚到簇级 latent graph，PreLNTransformerBlock 在簇空间建立长距离依赖，GraphViTDecoder 将全局信息回填到节点并预测状态增量。

### 适用场景

- 任务是二维非结构网格流体动力学时序预测。
- 数据包含节点坐标、三角网格、速度、压力、节点类型和有效节点 mask。
- 需要在大规模节点图上捕获远距离空间依赖，但直接全节点注意力成本过高。
- 已经有或可以生成 constrained k-means cluster 文件。
- 输出目标是节点级下一步或多步滚动状态预测。

不适合优先使用的情况：

- 数据是规则网格图像形式且无非结构拓扑，可优先考虑 FNO、U-Net、FourCastNet 类模型。
- 任务没有时间维或不需要自回归滚动。
- 无法提供 cluster 分配或节点类型字段，且短期内不准备改造 datapipe。
- 需要严格守恒或显式求解器约束，而当前训练目标仅以监督损失为主。

### 输入

决策前应收集：

- 数据根目录、split 目录和 cluster 目录。
- `sim.npz` 是否包含 `pointcloud/VX/VY/PS/PG/mask`。
- `triangles.npy` 是否可转换为边。
- `constrained_kmeans_<n_cluster>.npy` 是否存在且与配置一致。
- 状态通道定义：速度维度、压力维度和拼接后的 `state_size`。
- 节点类型是否为 one-hot，且维度是否为 9。
- 训练、验证、测试窗口长度。
- 资源预算：GPU 数量、显存、目标 batch size、训练时长。

### 输出

规划输出应包含：

- `model_choice`：是否选择 `GraphViT`。
- `datapipe_choice`：是否使用 `EagleDatapipe` 以及数据字段是否需要适配。
- `model_parameters`：`state_size`、`w_size`、`n_attention`、`nb_gn`、`n_heads`、`pos_length`。
- `data_parameters`：`window_length_train/val/test`、`n_cluster`、`normalized`、`type_as_onehot`、`with_cells`。
- `training_plan`：batch size、学习率、loss_alpha、patience、checkpoint_dir。
- `evaluation_plan`：N-RMSE 时间步、动画数量、checkpoint 加载路径。
- `risk_notes`：cluster、mask、shape、DDP checkpoint 和长程滚动误差风险。

### 执行流程

```text
1. 判断任务类型
  -> 是否为 mesh-based temporal CFD forecasting
  -> 是否需要节点级状态滚动预测

2. 检查 Eagle 数据协议
  -> split 文件是否存在
  -> sim.npz 和 triangles.npy 是否完整
  -> cluster 文件是否与 n_cluster 匹配
  -> node_type 是否可 one-hot 到 9 维

3. 配置 datapipe
  -> 设置 data_dir / cluster_dir / splits_dir
  -> 设置 window_length_train/val/test
  -> 设置 n_cluster、normalized、type_as_onehot、with_cells
  -> 验证 batch 输出字段和 shape

4. 配置 GraphViT
  -> state_size = velocity_dim + pressure_dim
  -> w_size 根据资源预算选择，默认 512
  -> n_attention 和 n_heads 保持 attention mask 维度兼容
  -> nb_gn 根据局部传播需求调整

5. 训练
  -> state = concat(velocity, pressure)
  -> model(..., apply_noise=True)
  -> 使用 output_hat 与 target 计算增量损失
  -> 使用反归一化后的 state_hat 计算速度和压力指标
  -> 按验证集 best loss 保存 checkpoint

6. 评估与可视化
  -> 加载 best_model.pth
  -> model(..., apply_noise=False)
  -> 计算逐时间步 N-RMSE
  -> 可选用 cells 生成流场动画
```

### 约束

- 不要把 graphViT 当作无 cluster 的普通 GNN 使用；cluster 是主架构的一部分。
- `n_attention` 与 `n_heads` 默认都为 4；若改动其中之一，需要验证 attention mask shape。
- `w_size + 4 * pos_length` 必须能被 `n_heads` 整除。
- `state_size` 改动必须同步到模型、loss、denormalize 和通道切分逻辑。
- `node_type` 索引语义固定：normal、disable、input、output、wall 会影响噪声注入和边界覆盖。
- 评估动画依赖 `cells`，若 `with_cells=False` 只能做数值评估或需另行构造三角面。
- 训练/评估默认依赖硬编码归一化统计量，跨数据集迁移时必须重新审查尺度。

### 下一阶段建议

- 若目标是复现实例：先使用默认 Eagle 配置运行训练或加载已有 checkpoint 做评估。
- 若目标是接入新 CFD 数据：先实现 EagleDatapipe 兼容字段或新 datapipe，确保输出字段与 GraphViT.forward 对齐。
- 若节点数很大：优先增加/调整 cluster 数量，而不是直接增大 Transformer 序列长度。
- 若长程预测误差增长快：增加训练窗口、使用 scheduled sampling、调低学习率或强化边界节点约束。
- 若局部细节不足：增加 `nb_gn` 或 Decoder 局部传播深度。
- 若全局依赖不足：增加 `n_attention`、`w_size` 或改进 cluster 构造质量。

### 回退策略

- 缺少 cluster 文件：先运行 clusterize 脚本或将配置改为已有的 `n_cluster`，不要直接绕过 pooling。
- 出现空 batch：检查 split 文件路径、样本目录和损坏样本，必要时先过滤数据。
- shape 不匹配：逐项打印 `mesh_pos/edges/state/node_type/clusters/clusters_mask` 的 batch shape，优先修复 datapipe。
- attention mask 报错：确认 `n_attention`、`n_heads`、`K` 和 mask reshape 逻辑一致。
- checkpoint 加载失败：区分包含 `model_state_dict` 的 checkpoint 和纯 state_dict，兼容 DDP 前缀。
- 新数据不适配 hard-coded normalization：先关闭归一化或重建统计量，再比较指标。

## 组件契约入口

- ../contracts/oneencoderstylegraphvitencoder.md
- ../contracts/onepoolingstylernnclusterpooling.md
- ../contracts/onetransformerstyleprelntransformerblock.md
- ../contracts/onedecoderstylegraphvitdecoder.md
- ../contracts/oneembeddingstylefourierposembedding.md
- ../contracts/eagledatapipe.md
- ../contracts/standardmlpgnnlayerscatter_sum.md

## 源码锚点

- `{onescience_path}/onescience/src/onescience/models/graphvit/graphViT.py`
