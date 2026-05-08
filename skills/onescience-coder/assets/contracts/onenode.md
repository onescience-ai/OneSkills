# Contract: OneNode

## 基本信息

- 组件名：`OneNode`
- 所属模块族：`node`
- 统一入口：`direct_import`
- 注册名：`style="<NodeStyle>"`

## 组件职责

为图神经网络中的节点更新模块提供统一注册入口。

补充说明：

- 调用层通过 `style` 选择具体 node block
- 当前 CFD 图模型最相关的 style 是 `MeshNodeBlock`
- 通常在边更新之后执行，聚合邻接边信息并更新节点隐状态

## 支持输入

- 图输入：`edge_features, node_features, graph`
- 结构化网格输入：`not_applicable`

内部统一做法：

- 先检查 `style` 是否已注册
- 再将构造参数透传给具体节点更新实现
- forward 时不负责构建邻接关系，只使用传入图对象中的拓扑

## 构造参数

- `style`
  - 具体节点更新实现的注册名，例如 `MeshNodeBlock`
- `aggregation`
  - 从边到节点的信息聚合方式，常见为 `sum` 或 `mean`
- `input_dim_nodes`
  - 输入节点特征维度
- `input_dim_edges`
  - 输入边特征维度
- `output_dim`
  - 输出节点特征维度
- `hidden_dim`
  - 节点更新 MLP 的隐藏维度
- `hidden_layers`
  - 节点更新 MLP 的层数

## 输出约定

- 图输出：通常返回更新后的 `edge_features, node_features`，真实返回格式以底层 block 为准
- 节点输出维度：节点特征最后一维通常为 `output_dim`

额外约束：

- 聚合方向由底层图对象和 block 实现决定，适配新图数据时必须确认边方向
- 节点更新不会自动处理边界条件，边界节点 mask 需要在模型或训练流程中单独处理

## 典型调用位置

- `MeshGraphNetProcessor`
- `MeshGraphNet` 的 processor block
- 非结构网格 CFD 或粒子系统中的节点状态更新

## 典型参数

- MeshGraphNet 节点更新
  - `style="MeshNodeBlock"`
  - `aggregation="sum"`
  - `input_dim_nodes=hidden_dim_processor`
  - `input_dim_edges=hidden_dim_processor`
  - `output_dim=hidden_dim_processor`

## 风险点

- `aggregation` 会影响长时间 rollout 的数值尺度，不能在复现实验时随意替换
- 节点特征和目标变量不一定同维，decoder 前后的维度约定要分开看
- 如果新数据集只有网格坐标而没有边，需要先补构图逻辑，不能只替换 `OneNode`

## 源码锚点

- `./onescience/src/onescience/modules/node/onenode.py`
- `./onescience/src/onescience/modules/node/mesh_node_block.py`
- `./onescience/src/onescience/models/meshgraphnet/meshgraphnet.py`
