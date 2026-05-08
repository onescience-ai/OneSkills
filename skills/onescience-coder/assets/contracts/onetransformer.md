# Contract: OneTransformer

## 基本信息

- 组件名：`OneTransformer`
- 所属模块族：`transformer`
- 统一入口：`direct_import`
- 注册名：`style="<TransformerStyle>"`

## 组件职责

为 transformer 类组件提供统一注册入口。

补充说明：

- 调用层通过 `style` 选择具体 transformer 实现
- 当前天气相关模型常通过它调用 `EarthTransformer2DBlock`、`EarthTransformer3DBlock`、`FuxiTransformer`
- wrapper 本身不规定固定 shape，真实规则来自具体实现

## 支持输入

- 2D 输入：`depends_on_style`
- 3D 输入：`depends_on_style`

内部统一做法：

- 先检查 `style` 是否已注册
- 再将构造参数透传给具体 transformer
- 前向时直接调用底层模块

## 构造参数

- `style`
  - 具体 transformer 实现的注册名
- `**kwargs`
  - 直接透传给对应 transformer 实现

## 输出约定

- 2D 输出：`depends_on_style`
- 3D 输出：`depends_on_style`

如果有明确边界条件，也写在这里：

- shape 约束以下层 transformer 契约为准
- 新 transformer 组件后需同步注册到 `onetransformer.py`

## 典型调用位置

- PanguFuser
- FengWuEncoder
- FengWuDecoder
- FengWuFuser
- Fuxi 主模型

## 典型参数

- 二维 Earth block
  - `style="EarthTransformer2DBlock"`
- 三维 Earth block
  - `style="EarthTransformer3DBlock"`
- Fuxi U-shape trunk
  - `style="FuxiTransformer"`

## CFD / 图模型补充

当前 CFD、图网络和神经算子相关模型还会通过 `OneTransformer` 调用以下 style：

- Transolver 系列
  - `style="Transolver_block"`
  - 典型位置：`Transolver2D / Transolver3D / Transolver*_plus`
  - 典型输入：点云或网格 token 的隐特征 `fx`
- CFD_Benchmark 注意力算子
  - `style="Galerkin_Transformer_block"`
  - `style="Factformer_block"`
  - `style="GNOTTransformerBlock"`
  - 典型输入：由坐标和物理量拼接后升维得到的 token 表示
- 神经谱块
  - `style="NeuralSpectralBlock1D"`
  - `style="NeuralSpectralBlock2D"`
  - `style="NeuralSpectralBlock3D"`
  - 典型输入：结构化网格特征，通常与 `U_NO` 类模型相关
- 图 ViT
  - `style="PreLNTransformerBlock"`
  - 典型输入：cluster 级 token `W`、`attention_mask` 和 cluster 位置编码
- 局部视觉块
  - `style="SwinTransformerBlock"`
  - 适合窗口化图像/网格特征，不应默认替代物理 attention block

补充约束：

- `Transolver_block / Galerkin_Transformer_block / Factformer_block` 都会在内部继续调用 `OneAttention` 和 `OneMlp`，调参时要同时核对 attention style
- `PreLNTransformerBlock` 是 GraphViT 的潜空间 cluster 交互层，不是普通 NLP Transformer block
- `NeuralSpectralBlock*d` 更接近神经算子 block，输入维度和 patch 参数要与网格维度匹配

## 风险点

- `OneTransformer` 只是分发入口，不代表统一的 tensor 语义
- `EarthTransformer2DBlock` 与 `FuxiTransformer` 都属于 transformer，但输入形态完全不同
- 只看 wrapper 无法判断是否需要先展平 token 或先恢复网格

## 源码锚点

- `./onescience/src/onescience/modules/transformer/onetransformer.py`
- `./onescience/src/onescience/modules/transformer/earthtransformer2Dblock.py`
- `./onescience/src/onescience/modules/transformer/earthtransformer3Dblock.py`
- `./onescience/src/onescience/modules/transformer/fuxitransformer.py`
- `./onescience/src/onescience/modules/transformer/Transolver_block.py`
- `./onescience/src/onescience/modules/transformer/Neural_Spectral_Block.py`
