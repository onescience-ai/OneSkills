# Contract: uma_radial.py

## 基本信息

- 组件名：`UMA Radial Family`
- 所属模块族：`materials / uma / layer`
- 统一入口：`direct_import`
- 注册名：`not_applicable`
- 主源码：`./onescience/src/onescience/modules/layer/uma_radial.py`

## 组件职责

提供 UMA 的高斯径向展开、包络函数和径向 MLP，用于将边距离映射为 eSCNMD block 可消费的边特征。

覆盖组件：

- `gaussian`
- `PolynomialEnvelope`
- `GaussianSmearing`
- `RadialMLP`

## 输入契约

- 边距离：`(NumEdges,)` 或 `(NumEdges, 1)`
- 标量边特征：`(NumEdges, EdgeChannels)`
- cutoff 语义来自 backbone 配置

## 输出契约

- 高斯基：`(NumEdges, NumGaussians)`
- envelope：可广播到边特征
- `RadialMLP` 输出：`(NumEdges, OutputChannels)`

## 关键参数

- `start`
- `stop`
- `num_gaussians`
- `basis_width_scalar`
- `cutoff`
- `hidden_channels`
- `out_channels`
- `activation`

## 典型调用位置

- `EdgeDegreeEmbedding`
- `eSCNMD_Block.Edgewise`
- UMA backbone forward

## 常见修改点

- 改 `cutoff/max_neighbors`：同步检查图构建、邻居分布和显存。
- 改高斯基数量：同步检查 edge channels list。
- 改 MLP 输出：同步检查 block 输入 edge channel。

## 风险点

- cutoff 与 `max_neighbors` 配合不当会导致过密图或丢邻居。
- 边距离单位错误会使径向基完全偏离训练分布。
- 改 edge channels 但不改 block 会造成 shape mismatch。
- 与 checkpoint 中的 radial 参数不一致通常不能直接加载权重。

## 源码锚点

- `./onescience/src/onescience/modules/layer/uma_radial.py`
- `./onescience/src/onescience/modules/embedding/uma_embedding.py`
- `./onescience/src/onescience/modules/block/uma_escn_md_block.py`

## 下钻关系

- 图构建：`./uma_graph_compute.md`
- embedding：`./uma_embedding.md`
- block：`./uma_escn_md_block.md`
