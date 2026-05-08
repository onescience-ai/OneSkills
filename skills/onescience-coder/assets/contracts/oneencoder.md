# Contract: OneEncoder

## 基本信息

- 组件名：`OneEncoder`
- 所属模块族：`encoder`
- 统一入口：`direct_import`
- 注册名：`style="<EncoderStyle>"`

## 组件职责

为编码器类组件提供统一注册入口。

补充说明：

- 调用层通过 `style` 选择具体 encoder 实现
- 当前天气相关模型最常用的是 `FengWuEncoder`
- wrapper 本身不定义固定 shape，真实规则来自具体 encoder

## 支持输入

- 2D 输入：`depends_on_style`
- 3D 输入：`depends_on_style`

内部统一做法：

- 先检查 `style` 是否已注册
- 再将构造参数透传给具体 encoder
- 前向时直接调用底层 encoder

## 构造参数

- `style`
  - 具体 encoder 实现的注册名
- `**kwargs`
  - 直接透传给对应 encoder 实现

## 输出约定

- 2D 输出：`depends_on_style`
- 3D 输出：`depends_on_style`

如果有明确边界条件，也写在这里：

- 真实 shape 约束以下层 encoder 契约为准
- 新 encoder 组件后需同步注册到 `oneencoder.py`

## 典型调用位置

- FengWu 主模型

## 典型参数

- FengWu 单分支编码
  - `style="FengWuEncoder"`

## CFD / 图模型补充

当前 CFD、DeepCFD、GraphViT 和 MeshGraphNet 相关模型还会通过 `OneEncoder` 调用以下 style：

- UNet 编码器
  - `style="UNetEncoder1D"`
  - `style="UNetEncoder2D"`
  - `style="UNetEncoder3D"`
  - 常见参数：`in_channels, base_channels, num_stages, bilinear, normtype, kernel_size`
  - 典型位置：`DeepCFD.UNet / UNetEx`、`cfdbench.unet`
- GraphViT 编码器
  - `style="GraphViTEncoder"`
  - 常见参数：`nb_gn, state_size, pos_length`
  - 典型输入：`mesh_pos, edges, states, node_type, pos_enc`
- MeshGraph 编码器
  - `style="MeshGraphEncoder"`
  - 面向图节点/边特征编码，使用前要回到源码确认当前模型是否直接调用

补充约束：

- UNet encoder 返回的是多尺度 skip feature 列表，通常必须交给匹配的 `UNetDecoder*d`
- GraphViT encoder 返回节点表示和边表示，不能直接接普通 CNN decoder
- 新数据集接入时，需要先判断是规则网格、非结构点云还是显式图结构，再选择 encoder family

## 风险点

- `OneEncoder` 只是入口，不表示所有 encoder 可互换
- 只看 wrapper 无法判断输出是 token、grid 还是多分支结构
- `style` 未注册时会直接报错

## 源码锚点

- `./onescience/src/onescience/modules/encoder/oneencoder.py`
- `./onescience/src/onescience/modules/encoder/fengwuencoder.py`
- `./onescience/src/onescience/modules/encoder/unet_encoder.py`
- `./onescience/src/onescience/modules/encoder/graphvit_encoder.py`
