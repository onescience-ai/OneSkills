# Contract: OneAttention

## 基本信息

- 组件名：`OneAttention`
- 所属模块族：`attention`
- 统一入口：`direct_import`
- 注册名：`style="<AttentionStyle>"`

## 组件职责

为 attention 类组件提供统一注册入口。

补充说明：

- 调用层通过 `style` 选择具体 attention 实现
- 当前天气相关模型最常见的是 `EarthAttention2D` 与 `EarthAttention3D`
- wrapper 本身不定义固定 shape，真实约束来自具体 attention 实现

## 支持输入

- 2D 输入：`depends_on_style`
- 3D 输入：`depends_on_style`

内部统一做法：

- 先检查 `style` 是否已注册
- 再将构造参数透传给具体 attention
- 前向时直接调用底层 attention

## 构造参数

- `style`
  - 具体 attention 实现的注册名
- `**kwargs`
  - 直接透传给对应 attention 实现

## 输出约定

- 2D 输出：`depends_on_style`
- 3D 输出：`depends_on_style`

如果有明确边界条件，也写在这里：

- 真实 shape 约束以下层 attention 契约为准
- 新 attention 组件后需同步注册到 `oneattention.py`

## 典型调用位置

- EarthTransformer2DBlock
- EarthTransformer3DBlock

## 典型参数

- 二维 Earth attention
  - `style="EarthAttention2D"`
- 三维 Earth attention
  - `style="EarthAttention3D"`

## CFD / 图模型补充

当前 CFD 神经算子与 Transolver 相关模型还会通过 `OneAttention` 调用以下 style：

- Transolver 物理注意力
  - `style="Physics_Attention_Irregular_Mesh"`
  - `style="Physics_Attention_Irregular_Mesh_plus"`
  - `style="Physics_Attention_Structured_Mesh_1D"`
  - `style="Physics_Attention_Structured_Mesh_2D"`
  - `style="Physics_Attention_Structured_Mesh_3D"`
  - 常见参数：`dim, heads, dim_head, dropout, slice_num, shapelist`
- Factformer / Galerkin / GNOT
  - `style="FactAttention2D"`
  - `style="FactAttention3D"`
  - `style="LinearAttention"`
  - `style="Vanilla_Linear_Attention"`
  - 常见参数：`dim, heads, dim_head, dropout`
- 窗口与通用注意力
  - `style="WindowAttention"`
  - `style="FlashAttention"`
  - `style="MultiHeadAttention"`
  - `style="SelfAttention"`
  - `style="NystromAttention"`

补充约束：

- Transolver 的 irregular / structured mesh attention 不是可随意互换的 attention；选择哪一个通常由 `space_dim`、`shapelist` 和数据是否结构化决定
- `LinearAttention` 在 GNOT / Galerkin block 中常用于自注意力和交叉注意力，forward 参数可能包含 `x, y, mask`
- `FactAttention2D/3D` 依赖 `shapelist` 表达空间维度，不能只看 token 数决定是否可用

## 风险点

- wrapper 不会帮调用层把原始网格转换为窗口化张量
- `EarthAttention2D` 与 `EarthAttention3D` 的输入 shape 不可互换
- 只看 wrapper 无法知道 mask 应该按什么窗口布局构造

## 源码锚点

- `./onescience/src/onescience/modules/attention/oneattention.py`
- `./onescience/src/onescience/modules/attention/earthattention2d.py`
- `./onescience/src/onescience/modules/attention/earthattention3d.py`
- `./onescience/src/onescience/modules/attention/physicsattention.py`
- `./onescience/src/onescience/modules/attention/linearattention.py`
