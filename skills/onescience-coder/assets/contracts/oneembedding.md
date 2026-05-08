# Contract: OneEmbedding

## 基本信息

- 组件名：`OneEmbedding`
- 所属模块族：`embedding`
- 统一入口：`direct_import`
- 注册名：`style="<EmbeddingStyle>"`

## 组件职责

为 embedding 类组件提供统一注册入口。

补充说明：

- 调用层通过 `style` 选择具体 embedding 实现
- 它本身不定义固定 shape 语义，真实约束来自被选中的具体组件
- 当前天气相关模型常通过它调用 `PanguEmbedding`、`FourCastNetEmbedding`、`FuxiEmbedding`

## 支持输入

- 2D 输入：`depends_on_style`
- 3D 输入：`depends_on_style`

内部统一做法：

- 先检查 `style` 是否已注册
- 再将构造参数透传给具体实现
- 前向时不改写输入输出 shape

## 构造参数

- `style`
  - 具体 embedding 实现的注册名
- `**kwargs`
  - 直接透传给对应 embedding 实现

## 输出约定

- 2D 输出：`depends_on_style`
- 3D 输出：`depends_on_style`

如果有明确边界条件，也写在这里：

- `style` 必须已在 `oneembedding.py` 注册
- shape 约束应以下层具体 embedding 契约为准

## 典型调用位置

- Pangu 主模型
- FourCastNet 主模型
- Fuxi 主模型
- FengWuEncoder

## 典型参数

- Pangu 2D / 3D patch embedding
  - `style="PanguEmbedding"`
- FourCastNet patch embedding
  - `style="FourCastNetEmbedding"`
- Fuxi 时空块 embedding
  - `style="FuxiEmbedding"`

## CFD / 图模型补充

当前 CFD 图模型中最相关的补充 style 是：

- GraphViT 位置编码
  - `style="FourierPosEmbedding"`
  - 常见参数：`pos_start, pos_length`
  - 典型输入：`mesh_pos, clusters, clusters_mask`
  - 典型输出：节点位置编码和 cluster 位置编码

补充说明：

- `FourierPosEmbedding` 不是常规 patch embedding，而是面向图节点和 cluster 的 Fourier 位置编码
- `CFD_Benchmark` 中部分模型直接使用 `onescience.modules.embedding` 下的函数式 `unified_pos_embedding`、`timestep_embedding`，它们不是 `OneEmbedding` 注册入口
- 判断新 CFD 数据是否适合 GraphViT 时，需要先确认 datapipe 能否提供 `clusters` 与 `clusters_mask`

## 风险点

- 不要把 `OneEmbedding` 当成具体实现本身
- 只看 wrapper 无法得到真实 shape 约束
- 新增 embedding 后若未注册，调用层即使写对构造参数也无法工作

## 源码锚点

- `./onescience/src/onescience/modules/embedding/oneembedding.py`
- `./onescience/src/onescience/modules/embedding/panguembedding.py`
- `./onescience/src/onescience/modules/embedding/fourcastnetembedding.py`
- `./onescience/src/onescience/modules/embedding/fuxiembedding.py`
- `./onescience/src/onescience/modules/embedding/fourier_pos_embedding.py`
