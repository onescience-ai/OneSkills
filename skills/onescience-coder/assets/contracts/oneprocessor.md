# Contract: OneProcessor

## 基本信息

- 组件名：`OneProcessor`
- 所属模块族：`processor`
- 统一入口：`direct_import`
- 注册名：`style="<ProcessorStyle>"`

## 组件职责

为图模型中的高阶 processor 提供统一注册入口。

补充说明：

- 调用层通过 `style` 选择具体图处理器
- 当前 CFD 图模型中主要用于 `BiStrideMeshGraphNet`
- 与 `OneEdge` / `OneNode` 这种单步 message passing block 不同，`OneProcessor` 更偏向完整的多尺度或层级处理流程

## 支持输入

- 图输入：`depends_on_style`
- 多尺度图输入：`h, m_ids, m_gs, pos`
- 结构化网格输入：`not_applicable`

内部统一做法：

- 先检查 `style` 是否已注册
- 再将构造参数透传给具体 processor
- forward 时只透传参数，不主动生成多尺度图或采样索引

## 构造参数

- `style`
  - 具体 processor 实现的注册名
- `unet_depth`
  - `BistrideGraphMessagePassing` 的多尺度深度
- `latent_dim`
  - 节点隐状态维度
- `hidden_layer`
  - processor 内部 MLP 或图卷积层的隐藏层设置
- `pos_dim`
  - 节点坐标维度，常见为 2 或 3

## 输出约定

- `BistrideGraphMessagePassing`：输入节点隐状态，输出同节点集合上的更新后隐状态
- `GraphMessagePassing`：在指定图和坐标上执行一层图信息传递

额外约束：

- 多尺度图索引 `m_ids`、多尺度边 `m_gs` 与节点坐标 `pos` 必须来自同一网格
- 该入口不负责从原始网格自动构建 BiStride 层级结构

## 典型调用位置

- `BiStrideMeshGraphNet`
- 需要在 MeshGraphNet 平坦 processor 之后加入层级多尺度信息传递的 CFD 图代理任务

## 典型参数

- BiStride processor
  - `style="BistrideGraphMessagePassing"`
  - `unet_depth=num_mesh_levels`
  - `latent_dim=hidden_dim_processor`
  - `hidden_layer=num_layers_bistride`
  - `pos_dim=bistride_pos_dim`

## 风险点

- `OneProcessor` 的输入语义比普通 `OneEdge` / `OneNode` 更强，必须确认多尺度图数据已经由 datapipe 或预处理脚本提供
- `pos_dim` 要与真实网格坐标维度一致，2D 翼型和 3D 体/面网格不能混用默认值
- 如果任务只是标准 MeshGraphNet message passing，优先看 `OneEdge` / `OneNode`，不要误用 BiStride processor

## 源码锚点

- `./onescience/src/onescience/modules/processor/oneprocessor.py`
- `./onescience/src/onescience/modules/processor/bistride_processor.py`
- `./onescience/src/onescience/models/meshgraphnet/bsms_mgn.py`
