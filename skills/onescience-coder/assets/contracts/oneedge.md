# Contract: OneEdge

## 基本信息

- 组件名：`OneEdge`
- 所属模块族：`edge`
- 统一入口：`direct_import`
- 注册名：`style="<EdgeStyle>"`

## 组件职责

为图神经网络中的边更新模块提供统一注册入口。

补充说明：

- 调用层通过 `style` 选择具体 edge block
- 当前 CFD 图模型最相关的 style 是 `MeshEdgeBlock`
- 通常处于 MeshGraphNet 的 message passing / processor 阶段，负责根据边特征、相邻节点特征和图拓扑更新边表示

## 支持输入

- 图输入：`edge_features, node_features, graph`
- 结构化网格输入：`not_applicable`

内部统一做法：

- 先检查 `style` 是否已注册
- 再将构造参数透传给具体边更新实现
- forward 时不改写图对象、边索引或节点顺序

## 构造参数

- `style`
  - 具体边更新实现的注册名，例如 `MeshEdgeBlock`
- `input_dim_nodes`
  - 输入节点特征维度
- `input_dim_edges`
  - 输入边特征维度
- `output_dim`
  - 输出边特征维度
- `hidden_dim`
  - 边更新 MLP 的隐藏维度
- `hidden_layers`
  - 边更新 MLP 的层数
- `aggregation / do_concat_trick / norm_type / activation_fn`
  - 由具体 `MeshEdgeBlock` 使用，跨模型复用时以源码调用点为准

## 输出约定

- 图输出：通常返回更新后的 `edge_features` 与原节点特征，真实返回格式以底层 block 为准
- 输出维度：边特征最后一维通常为 `output_dim`

额外约束：

- `graph` 必须包含和 `edge_features` 对齐的边顺序
- `node_features` 的节点数必须和 `graph` 的节点数一致
- 该入口不负责构图、补边或 batch 图拼接

## 典型调用位置

- `MeshGraphNetProcessor`
- `MeshGraphNet` 的 Encode-Process-Decode 中间处理阶段
- 需要显式边更新的非结构网格 CFD 代理模型

## 典型参数

- MeshGraphNet 边更新
  - `style="MeshEdgeBlock"`
  - `input_dim_nodes=hidden_dim_processor`
  - `input_dim_edges=hidden_dim_processor`
  - `output_dim=hidden_dim_processor`
  - `norm_type="LayerNorm"`

## 风险点

- `OneEdge` 只负责分发，不代表所有图数据都可以直接接入；调用层必须先保证图拓扑和特征顺序一致
- `MeshEdgeBlock` 依赖 DGL 图或兼容图结构，普通张量不能直接替代 `graph`
- 边特征维度和节点特征维度经常相同但不是同一语义，适配新数据集时不要混用

## 源码锚点

- `./onescience/src/onescience/modules/edge/oneedge.py`
- `./onescience/src/onescience/modules/edge/mesh_edge_block.py`
- `./onescience/src/onescience/models/meshgraphnet/meshgraphnet.py`
