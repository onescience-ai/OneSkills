# Contract: OnePooling

## 基本信息

- 组件名：`OnePooling`
- 所属模块族：`pooling`
- 统一入口：`direct_import`
- 注册名：`style="<PoolingStyle>"`

## 组件职责

为图或点集特征的池化模块提供统一注册入口。

补充说明：

- 调用层通过 `style` 选择具体 pooling 实现
- 当前 CFD 图模型最相关的 style 是 `RNNClusterPooling`
- 常用于 GraphViT 中从节点级表示聚合到 cluster 级潜空间 token

## 支持输入

- 图节点输入：`V, clusters, positional_encoding, cluster_mask`
- 结构化网格输入：`not_applicable`

内部统一做法：

- 先检查 `style` 是否已注册
- 再将构造参数透传给具体 pooling 实现
- forward 时不重新计算 cluster，只使用 datapipe 或预处理阶段提供的 cluster 索引和 mask

## 构造参数

- `style`
  - 具体 pooling 实现的注册名，例如 `RNNClusterPooling`
- `w_size`
  - cluster 级潜空间特征维度
- `pos_length`
  - 位置编码维度

## 输出约定

- 输入节点特征：通常为 `V`
- 输入 cluster 索引：通常为 `clusters`
- 输出 cluster token：通常为 `W`
- 真实 shape 以底层 `RNNClusterPooling` 和调用模型为准

额外约束：

- `clusters` 与 `cluster_mask` 必须一一对应
- cluster 中的节点索引必须落在当前样本节点数范围内
- 该入口不负责点云聚类或网格 coarsening

## 典型调用位置

- `GraphViT.graph_pooling`
- 图网格 CFD 的节点表示到潜空间 token 压缩阶段

## 典型参数

- GraphViT pooling
  - `style="RNNClusterPooling"`
  - `w_size=512`
  - `pos_length=8`

## 风险点

- `OnePooling` 不等价于 CNN pooling；它依赖显式 cluster 索引和 mask
- 新数据集接 GraphViT 时，datapipe 需要同时提供节点、边、cluster 和 cluster mask
- cluster 数量和每个 cluster 最大节点数变化时，要先确认训练代码的 batch collate 是否支持 padding

## 源码锚点

- `./onescience/src/onescience/modules/pooling/onepooling.py`
- `./onescience/src/onescience/modules/pooling/rnn_cluster_pooling.py`
- `./onescience/src/onescience/models/graphvit/graphViT.py`
