# Model Card: BE_MPNN

## 基本信息

- 模型名：`BE_MPNN`
- 任务类型：`cfd / model`
- 当前状态：`public`
- 主实现文件：`{onescience_path}/onescience/src/onescience/models/beno/BE_MPNN.py`

## 模型架构概览

BE_MPNN 的主模型类为 `HeteroGNS`，是 BENO（Boundary-Embedded Neural Operator）任务中的边界条件感知异构图消息传递网络。它服务于椭圆型 PDE 代理建模：输入由 BENO datapipe 生成的 `HeteroData`，其中 `G1` 表示场/区域分支，`G2` 表示边界条件分支，模型通过共享结构但参数独立的双图分支学习域内 forcing、几何距离、边界条件与解场之间的映射。

组件定位概括：该组件不是通用分子或蛋白 MPNN，而是面向 PDE 图样本的边界嵌入图神经算子。其关键特征是将边界点序列编码为全局边界向量，并在每轮节点更新中与邻域聚合消息一起注入，从而把复杂边界形状和边界值纳入解场预测。

## 参数规模

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

## 架构结构

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

## 输入模式

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

## 输出模式

```text
u: (NumNodes, nnode_out_features)
  默认 nnode_out_features=1
  表示采样节点处预测的标量 PDE 解场
```

训练示例中 `u` 会与 `data["G1+2"].y` 对齐计算 MSE；评估和推理阶段通常使用 datapipe 提供的 `u_normalizer.decode(...)` 将输出恢复到原始物理尺度。

## 形状变换

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

## 常见修改点

- 输入特征维度：当 datapipe 修改 `G1.x/G2.x` 的字段拼接方式时，同步修改 `nnode_in_features`。
- 边特征维度：当 `MeshGenerator.attributes(...)` 输出字段变化时，同步修改 `nedge_in_features`。
- 边界编码方式：可在 `InteractionNetwork.boundary_fn` 中替换或扩展 Transformer，例如加入边界类型 embedding、位置归一化或更强的序列池化。
- 消息传递深度：通过 `nmessage_passing_steps` 调整长程传播能力和计算成本。
- MLP 宽度与深度：通过 `mlp_hidden_dim`、`nmlp_layers` 调整表达能力。
- 分支融合方式：当前 Decoder 使用 `decoded_G1 + decoded_G2`，可改为 concat 后 MLP、门控融合或注意力融合，以增强场分支与边界分支交互。
- 残差策略：当前节点和边都使用简单残差相加，若训练不稳定可加入 dropout、残差缩放或 pre-normalization。

## 实现风险

- `boundary_fn` 固定以 `enc_in=3` 构造，边界张量最后一维必须为 3，否则会在卷积 token embedding 处报 shape 错误。
- `boundary.repeat(x.shape[0], 1)` 假定每个图样本的边界编码已经池化为 `(1, boundary_dim)`；批量图合并后若多个样本边界被拼成非预期结构，边界向量可能无法逐图对应。
- `trans_layer` 在配置注释中可能被误写为“消息传递层数”，但源码中它实际控制边界 Transformer encoder 层数；消息传递步数由 `nmessage_passing_steps` 控制，示例实例化未显式传入时使用默认 10。
- Processor 中 G1/G2 两套 `InteractionNetwork` 参数互不共享，修改一侧结构时应同步考虑另一侧。
- Decoder 直接相加两个分支输出，要求 `G1` 和 `G2` 的节点顺序与节点数一致。
- BENO datapipe 对边界点数、网格分辨率、RHS/SOL/BC 列语义存在默认假设，模型本身不做输入校验。
- 源码中 `from .transformer import *` 与未使用的 `pdb` 会增加命名污染和维护噪声。

## 启动方式

该模型通常通过 Python API 在 BENO 训练/推理脚本中启动，由配置文件 `conf/beno.yaml` 提供数据、模型和训练参数。

单卡训练示例：

```sh
cd {onescience_path}/onescience/examples/cfd/BENO
python train.py
```

多卡训练示例：

```sh
cd {onescience_path}/onescience/examples/cfd/BENO
torchrun --standalone --nnodes=1 --nproc_per_node=4 train.py
```

推理与结果绘图示例：

```sh
cd {onescience_path}/onescience/examples/cfd/BENO
python inference.py
```

Python API 最小调用示例：

```python
import torch.nn as nn
from onescience.models.beno.BE_MPNN import HeteroGNS

model = HeteroGNS(
    nnode_in_features=10,
    nnode_out_features=1,
    nedge_in_features=7,
    latent_dim=128,
    nmessage_passing_steps=10,
    nmlp_layers=2,
    mlp_hidden_dim=128,
    activation=nn.ReLU,
    boundary_dim=128,
    trans_layer=3,
)

out = model(batch)
```

## 输入模式

数据准备以 BENO datapipe 为主，原始文件默认组织如下：

```text
data_dir/
  RHS_<file_prefix>_all.npy
  SOL_<file_prefix>_all.npy
  BC_<file_prefix>_all.npy
```

示例配置默认参数：

- `datapipe.source.data_dir="${ONESCIENCE_DATASETS_DIR}/BENO/data/Dirichlet/"`
- `datapipe.source.cache_dir="./cache_data/"`
- `datapipe.source.file_prefix="N32_4c"`
- `datapipe.data.ntrain=900`
- `datapipe.data.ntest=100`
- `datapipe.data.resolution=32`
- `datapipe.data.ns=10`
- `datapipe.data.domain_bounds=[[0, 1], [0, 1]]`
- `datapipe.dataloader.batch_size=1`
- `datapipe.dataloader.num_workers=0`
- `datapipe.dataloader.pin_memory=True`

模型默认参数：

- `nnode_in_features=10`（示例配置）
- `nnode_out_features=1`（示例配置）
- `nedge_in_features=7`（示例配置）
- `latent_dim=128`（源码默认）
- `nmessage_passing_steps=10`（源码默认）
- `nmlp_layers=2`（源码默认与示例配置一致）
- `mlp_hidden_dim=128`（源码默认）
- `activation=nn.ELU`（源码默认；示例配置 `act="relu"` 会映射为 `nn.ReLU`）
- `boundary_dim=128`（源码默认与示例配置一致）
- `trans_layer=3`（源码默认与示例配置一致）

模型运行时输入字段：

```text
batch["G1"].x
batch["G1"].edge_index
batch["G1"].edge_features
batch["G1"].boundary
batch["G2"].x
batch["G2"].edge_index
batch["G2"].edge_features
batch["G2"].boundary
batch["G1+2"].y
```

其中 `batch["G1+2"].y` 不进入模型 forward，但用于训练损失和评估。

## 运行时接口

- `HeteroGNS.forward(data)`：接收 BENO 异构图 batch，返回节点级解场预测。
- `Encoder.forward(x, edge_features, x_inbd, edge_inbd_features)`：将 G1/G2 节点和边特征投影到 latent 空间。
- `Processor.forward(...)`：执行 G1/G2 两个分支的多步消息传递。
- `InteractionNetwork.forward(x, edge_index, edge_features, boundary)`：执行单步边界条件感知的图消息传递。
- `Decoder.forward(x, x_inbd)`：分别解码两个分支并求和得到最终节点输出。

## 主要函数

- `forward`
- `message`
- `update`

## 执行资源

- 设备：支持 CPU 与 GPU；训练建议使用 GPU。
- 显存/内存：主要由图节点数、边数、batch size、消息传递步数和边界 Transformer 层数决定。
- 数据：BENO datapipe 初始化会加载并预处理 `RHS/SOL/BC` 数组，首次构图会生成 `.pt` 缓存，`cache_dir` 需要可写。
- 分布式：示例训练脚本支持 `DistributedManager` 和 DDP，可通过 `torchrun` 或 `mpirun` 启动。
- 环境变量：示例配置依赖 `ONESCIENCE_DATASETS_DIR` 定位数据集根目录。
- 训练默认设置：`epochs=1000`、`optimizer=Adam`、`lr=1.0e-5`、`weight_decay=5.0e-4`、`scheduler=CosineAnnealingWarmRestarts`、`T_0=16`、`T_mult=2`、`save_period=1`。

## 运行限制

- 输入必须遵循 BENO datapipe 的异构图协议；普通张量不能直接传入 `HeteroGNS.forward`。
- 边界张量最后一维必须为 3，并能被边界 Transformer 解释为边界坐标和边界值序列。
- `G1` 与 `G2` 的节点数量和节点顺序应一致，因为 Decoder 直接相加两个分支的节点输出。
- 示例推理脚本按 `resolution * resolution` 重建完整网格，并默认 test batch size 适合逐样本重建；扩大 batch 时需检查索引回填逻辑。
- 当前实现更适配二维椭圆型 PDE 与 BENO 数据格式；迁移到三维、多物理量输出或时序 PDE 时，需要同步改造 datapipe、边界编码和输出头。
- 常见失败模式包括：`boundary` shape 不匹配、`edge_features` 维度与 `nedge_in_features` 不一致、缓存数据与当前配置不一致、checkpoint 参数名与 DDP 包装状态不一致、训练目标归一化与推理反归一化尺度不一致。

## 规划决策

### 描述

BE_MPNN 的规划决策重点是判断当前任务是否属于 BENO 风格的边界条件感知 PDE 代理求解，并在数据协议、模型结构和训练/推理脚本之间保持一致。该模型适合作为 BENO datapipe 的下游主模型：用 `G1` 建模域内 forcing 与几何特征，用 `G2` 建模边界条件分支，通过边界 Transformer 将边界点序列变成全局调制信息，再由图消息传递预测节点解场。

### 适用场景

- 任务是二维椭圆型 PDE、Poisson/Dirichlet/Neumann 类问题或类似边界条件驱动的解场预测。
- 数据可以被组织为 `RHS/SOL/BC` 三类数组，并由 BENO datapipe 构造为 `G1/G2/G1+2` 异构图。
- 需要显式利用复杂边界形状、边界点序列和非均匀边界值。
- 输出目标是采样节点处的标量或少量通道解场。
- 希望使用消息传递网络处理不规则采样节点和邻接边特征。

不宜优先使用的情况：

- 输入是规则网格且无复杂边界条件，可优先考虑 FNO、U-FNO、UNO 等规则网格神经算子。
- 任务是蛋白质、分子、气象或通用图分类，BE_MPNN 的输入协议和边界嵌入假设并不匹配。
- 数据无法提供边界点序列或 `G1/G2` 双分支图结构。

### 输入

决策前应确认：

- PDE 类型：是否为 BENO 适配的 elliptic PDE 或边界驱动问题。
- 原始数据：是否有 `RHS_<prefix>_all.npy`、`SOL_<prefix>_all.npy`、`BC_<prefix>_all.npy`。
- 数据字段：RHS 坐标列、forcing 列、cell_state 列和 SOL 目标列是否与 datapipe 约定一致。
- 边界条件：边界点数、边界坐标和值是否可形成 `(BoundaryNodes, 3)`。
- 图规模：`resolution`、`ns`、节点数、边数和 batch size。
- 输出要求：预测标量解场还是多通道解场。
- 运行模式：训练、推理、评估、可视化或模型结构改造。

### 输出

规划输出应包含：

- `model_choice`：是否选择 `HeteroGNS/BE_MPNN` 作为主模型。
- `datapipe_choice`：是否使用 `BENODatapipe` 以及需要修改的数据字段。
- `model_parameters`：`nnode_in_features`、`nedge_in_features`、`nnode_out_features`、`latent_dim`、`nmessage_passing_steps`、`boundary_dim`、`trans_layer`。
- `training_entry`：训练脚本、配置文件、checkpoint 输出目录。
- `inference_entry`：推理脚本、checkpoint 加载策略、结果重建方式。
- `risk_notes`：shape、归一化、边界维度、缓存一致性和分布式运行风险。

### 执行流程

```text
1. 识别任务
  -> 是否是边界条件驱动的 PDE surrogate
  -> 是否需要不规则域或复杂边界建模

2. 检查数据协议
  -> RHS/SOL/BC 文件是否齐备
  -> file_prefix、resolution、ntrain、ntest 是否与文件内容匹配
  -> 边界字段是否能形成 (BoundaryNodes, 3)

3. 构造或复用 BENODatapipe
  -> 生成 HeteroData
  -> 检查 G1/G2 节点特征维度
  -> 检查 edge_features 维度
  -> 检查 G1+2.y 与模型输出节点顺序一致

4. 配置 BE_MPNN
  -> nnode_in_features = G1.x.shape[-1]
  -> nedge_in_features = G1.edge_features.shape[-1]
  -> nnode_out_features = 目标通道数
  -> 根据显存预算调整 latent_dim 和 nmessage_passing_steps
  -> 根据边界复杂度调整 boundary_dim 和 trans_layer

5. 训练与评估
  -> 使用 model(batch) 得到节点输出
  -> 与 batch["G1+2"].y 计算训练损失
  -> 使用 u_normalizer.decode 恢复物理尺度后计算 L2/MAE
  -> 按 save_period 保存 checkpoint

6. 推理与重建
  -> 加载最新或指定 checkpoint
  -> 对 test_loader 前向预测
  -> 用 sample_idx 回填到 resolution x resolution 网格
  -> 解码并输出图像或数组结果
```

### 约束

- 文件落地与配置应保持 BENO 示例目录约定，避免把模型路径写死到业务字段中。
- 模型 `forward` 不负责数据校验；调用前必须保证 `G1/G2` 字段完整。
- `boundary` 最后一维固定匹配边界 Transformer 的 `enc_in=3`。
- `trans_layer` 仅控制边界 Transformer 深度；不要把它当作消息传递步数。
- 修改 datapipe 字段后，必须同步修改模型输入维度与训练脚本中配置。
- 多通道输出需要同步修改 `nnode_out_features`、目标 `y` shape、loss reshape 和推理回填逻辑。
- 若使用缓存，配置变化后应确保旧 `.pt` 缓存不会被误用。

### 下一阶段建议

- 若当前任务只是运行 BENO 示例：优先使用现有 `train.py`、`inference.py` 和 `conf/beno.yaml`，只修改数据路径、样本数和输出目录。
- 若当前任务是新 PDE 数据接入：先改造或复用 `BENODatapipe`，确保输出图协议与 BE_MPNN 对齐，再训练模型。
- 若边界条件更复杂：优先扩展边界特征和 `boundary_fn`，并保持 `(BoundaryNodes, C)` 到全局边界向量的清晰映射；若 C 不再等于 3，同步修改 Transformer `enc_in`。
- 若误差集中在复杂几何附近：尝试增加 `boundary_dim`、`nmessage_passing_steps`、边界采样密度或在 Decoder 引入门控融合。
- 若训练不稳定：降低学习率、检查 normalizer、增加残差正则或减少消息传递深度。

### 回退策略

- 当 `HeteroData` 字段不完整时：先回退到 datapipe 诊断，打印 `G1/G2/G1+2` 的字段与 shape。
- 当边界 shape 不匹配时：先在数据层将边界坐标和值整理为 `(BoundaryNodes, 3)`；若业务确实需要更多边界通道，再改造 `InteractionNetwork.boundary_fn`。
- 当缓存与配置不一致时：清理或更换 `cache_dir`，重新预处理。
- 当 checkpoint 加载失败时：区分 DDP 与非 DDP state_dict，必要时剥离或补充 `module.` 前缀。
- 当 BE_MPNN 表达能力不足时：先调大 latent/message passing/boundary encoder，再考虑替换分支融合或引入其他神经算子。
- 当任务不满足 BENO 图协议时：不要强行调用 BE_MPNN，改选规则网格神经算子或先实现适配 datapipe。

## 组件契约入口

- ../contracts/torch.nn.md
- ../contracts/torch_geometric.nn.messagepassing.md
- ../contracts/onescience.models.beno.transformer.transformer.md
- ../contracts/benodatapipe.md
- ../contracts/lploss__normalizer.md

## 源码锚点

- `{onescience_path}/onescience/src/onescience/models/beno/BE_MPNN.py`
