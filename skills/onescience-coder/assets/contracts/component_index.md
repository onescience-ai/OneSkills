# Component Index

## 目标

本文件是当前目录下组件契约的统一入口索引。

作用不是复述源码，而是帮助用户与智能体快速回答下面几个问题：

1. 当前任务应该先看哪个模块族
2. 某个组件应该从哪个 `One*` 入口初始化
3. `style` 应该写什么
4. 当前推荐优先使用哪些组件
5. 契约不足时，下一步应继续看哪一层

## 使用方式

建议按下面顺序检索：

1. 先根据任务语义，确定要查看的模块族
2. 先看高层业务组件，再决定是否继续下钻
3. 只有当高层组件不足以覆盖任务时，再看 `One*` 入口或底层模块
4. 契约仍不足时，再回到 `./onescience/` 对应源码锚点

默认不要一开始就直接检索底层 block 或 attention。

## 分层说明

当前索引按三层组织：

1. 统一入口层
   - `One*` 组件
   - 作用是统一调度、按 `style` 分发、提供调用入口
2. 高层业务组件层
   - 任务里最常直接拼装、替换、组合的组件
3. 底层通用模块层
   - block / attention / afno / fc 等下层实现单元

这三层在目录中保持平铺，在索引中进行逻辑分层。

## 统一入口层

| 组件 | 模块族 | 角色 | 注册方式 | 当前状态 | 契约卡片 |
|---|---|---|---|---|---|
| OneEmbedding | embedding | 统一 embedding 入口 | `style="<EmbeddingStyle>"` | `stable` | `./oneembedding.md` |
| OneSample | sample | 统一采样入口 | `style="<SampleStyle>"` | `stable` | `./onesample.md` |
| OneRecovery | recovery | 统一恢复入口 | `style="<RecoveryStyle>"` | `stable` | `./onerecovery.md` |
| OneFuser | fuser | 统一主干融合入口 | `style="<FuserStyle>"` | `stable` | `./onefuser.md` |
| OneEncoder | encoder | 统一 encoder 入口 | `style="<EncoderStyle>"` | `stable` | `./oneencoder.md` |
| OneDecoder | decoder | 统一 decoder 入口 | `style="<DecoderStyle>"` | `stable` | `./onedecoder.md` |
| OneTransformer | transformer | 统一 transformer 入口 | `style="<TransformerStyle>"` | `stable` | `./onetransformer.md` |
| OneAttention | attention | 统一 attention 入口 | `style="<AttentionStyle>"` | `stable` | `./oneattention.md` |
| OneAFNO | afno | 统一 AFNO 入口 | `style="<AFNOStyle>"` | `stable` | `./oneafno.md` |
| OneFC | fc | 统一前馈层入口 | `style="<FCStyle>"` | `stable` | `./onefc.md` |
| OneMlp | mlp | 统一 MLP 入口 | `style="<MlpStyle>"` | `stable` | `./onemlp.md` |
| OneFourier | fourier | 统一谱算子入口 | `style="<FourierStyle>"` | `stable` | `./onefourier.md` |
| OneHead | head | 统一预测头入口 | `style="<HeadStyle>"` | `stable` | `./onehead.md` |
| OnePooling | pooling | 统一图池化入口 | `style="<PoolingStyle>"` | `stable` | `./onepooling.md` |
| OneProcessor | processor | 统一图处理器入口 | `style="<ProcessorStyle>"` | `stable` | `./oneprocessor.md` |
| OneEdge | edge | 统一边更新入口 | `style="<EdgeStyle>"` | `stable` | `./oneedge.md` |
| OneNode | node | 统一节点更新入口 | `style="<NodeStyle>"` | `stable` | `./onenode.md` |
| OneEquivariant | equivariant | 统一等变层入口 | `style="<EquivariantStyle>"` | `stable` | `./oneequivariant.md` |

## 高层业务组件层

这些组件更适合作为任务实现、模型拼装、模块替换时的优先检索对象。

| 组件 | 模块族 | 调用入口 | 注册名 | 输入形态摘要 | 当前状态 | 契约卡片 |
|---|---|---|---|---|---|---|
| PanguEmbedding | embedding | `OneEmbedding` | `PanguEmbedding` | 2D 场 / 3D 场 | `stable` | `./panguembedding.md` |
| FourCastNetEmbedding | embedding | `OneEmbedding` | `FourCastNetEmbedding` | 2D 场 | `stable` | `./fourcastnetembedding.md` |
| FuxiEmbedding | embedding | `OneEmbedding` | `FuxiEmbedding` | 3D 时空块 | `stable` | `./fuxiembedding.md` |
| PanguDownSample | sample | `OneSample` | `PanguDownSample` | 2D token / 3D token | `stable` | `./pangudownsample.md` |
| PanguUpSample | sample | `OneSample` | `PanguUpSample` | 2D token / 3D token | `stable` | `./panguupsample.md` |
| FuxiDownSample | sample | `OneSample` | `FuxiDownSample` | 2D 特征图 | `stable` | `./fuxidownsample.md` |
| FuxiUpSample | sample | `OneSample` | `FuxiUpSample` | 2D 特征图 | `stable` | `./fuxiupsample.md` |
| PanguPatchRecovery | recovery | `OneRecovery` | `PanguPatchRecovery` | 2D 特征图 / 3D 特征图 | `stable` | `./pangupatchrecovery.md` |
| PanguFuser | fuser | `OneFuser` | `PanguFuser` | 3D token | `stable` | `./pangufuser.md` |
| FourCastNetFuser | fuser | `OneFuser` | `FourCastNetFuser` | 2D patch 网格特征 | `stable` | `./fourcastnetfuser.md` |
| FengWuFuser | fuser | `OneFuser` | `FengWuFuser` | 3D token | `stable` | `./fengwufuser.md` |
| FengWuEncoder | encoder | `OneEncoder` | `FengWuEncoder` | 2D 场 | `stable` | `./fengwuencoder.md` |
| FengWuDecoder | decoder | `OneDecoder` | `FengWuDecoder` | 中分辨率 token + 高分辨率 skip | `stable` | `./fengwudecoder.md` |
| FuxiTransformer | transformer | `OneTransformer` | `FuxiTransformer` | 2D 特征图 | `stable` | `./fuxitransformer.md` |
| UNetEncoder1D/2D/3D | encoder | `OneEncoder` | `UNetEncoder*d` | 规则网格多尺度特征 | `stable` | `./oneencoder.md` |
| UNetDecoder1D/2D/3D | decoder | `OneDecoder` | `UNetDecoder*d` | UNet skip feature 列表 | `stable` | `./onedecoder.md` |
| UNetHead1D/2D/3D | head | `OneHead` | `UNetHead*d` | 规则网格输出通道投影 | `stable` | `./onehead.md` |
| GraphViTEncoder | encoder | `OneEncoder` | `GraphViTEncoder` | 图节点、边、状态、位置编码 | `stable` | `./oneencoder.md` |
| RNNClusterPooling | pooling | `OnePooling` | `RNNClusterPooling` | 节点到 cluster token | `stable` | `./onepooling.md` |
| GraphViTDecoder | decoder | `OneDecoder` | `GraphViTDecoder` | cluster token 到节点状态增量 | `stable` | `./onedecoder.md` |
| MeshEdgeBlock | edge | `OneEdge` | `MeshEdgeBlock` | DGL 图边更新 | `stable` | `./oneedge.md` |
| MeshNodeBlock | node | `OneNode` | `MeshNodeBlock` | DGL 图节点更新 | `stable` | `./onenode.md` |
| BistrideGraphMessagePassing | processor | `OneProcessor` | `BistrideGraphMessagePassing` | 多尺度图 message passing | `stable` | `./oneprocessor.md` |
| GroupEquivariantConv2d/3d | equivariant | `OneEquivariant` | `GroupEquivariantConv*d` | GFNO 等变卷积 stem | `stable` | `./oneequivariant.md` |

## 底层通用模块层

这些组件通常作为继续下钻时的第二优先级，不建议替代高层业务组件成为默认起点。

| 组件 | 模块族 | 调用入口 | 注册名 | 输入形态摘要 | 当前状态 | 契约卡片 |
|---|---|---|---|---|---|---|
| EarthTransformer2DBlock | transformer | `OneTransformer` | `EarthTransformer2DBlock` | 2D token | `stable` | `./earthtransformer2dblock.md` |
| EarthTransformer3DBlock | transformer | `OneTransformer` | `EarthTransformer3DBlock` | 3D token | `stable` | `./earthtransformer3dblock.md` |
| EarthAttention2D | attention | `OneAttention` | `EarthAttention2D` | 2D 窗口化 token | `stable` | `./earthattention2d.md` |
| EarthAttention3D | attention | `OneAttention` | `EarthAttention3D` | 3D 窗口化 token | `stable` | `./earthattention3d.md` |
| FourCastNetAFNO2D | afno | `OneAFNO` | `FourCastNetAFNO2D` | 2D patch 网格特征 | `stable` | `./fourcastnetafno.md` |
| FourCastNetFC | fc | `OneFC` | `FourCastNetFC` | 任意前缀维度的特征张量 | `stable` | `./fourcastnetfc.md` |
| FuxiFC | fc | `OneFC` | `FuxiFC` | 任意前缀维度的特征张量 | `stable` | `./fuxifc.md` |
| Transolver_block | transformer | `OneTransformer` | `Transolver_block` | 点云/网格 token 隐特征 | `stable` | `./onetransformer.md` |
| Galerkin_Transformer_block | transformer | `OneTransformer` | `Galerkin_Transformer_block` | CFD token 序列 | `stable` | `./onetransformer.md` |
| Factformer_block | transformer | `OneTransformer` | `Factformer_block` | CFD token 序列 | `stable` | `./onetransformer.md` |
| PreLNTransformerBlock | transformer | `OneTransformer` | `PreLNTransformerBlock` | GraphViT cluster token | `stable` | `./onetransformer.md` |
| FNOSpectralConv*d | fourier | `OneFourier` | `FNOSpectralConv*d` | 规则网格谱卷积 | `stable` | `./onefourier.md` |
| GeoSpectralConv*d | fourier | `OneFourier` | `GeoSpectralConv*d` | 非结构点到规则潜网格投影 | `stable` | `./onefourier.md` |
| GSpectralConv*d | fourier | `OneFourier` | `GSpectralConv*d` | group-equivariant 谱卷积 | `stable` | `./onefourier.md` |
| Physics Attention | attention | `OneAttention` | `Physics_Attention_*` | Transolver 物理 attention | `stable` | `./oneattention.md` |
| Linear / Fact Attention | attention | `OneAttention` | `LinearAttention / FactAttention*d` | 神经算子 attention block | `stable` | `./oneattention.md` |

## 按模块族检索

### embedding

适用于：

- patch embedding
- 输入变量编码
- 2D 场或 3D 场的初始 token 化

优先顺序：

1. 先看高层 embedding 组件
2. 再看 `OneEmbedding`

### fuser

适用于：

- 主干特征提取
- token 融合
- trunk 建模
- surface 与 upper-air 联合建模
- 3D token 主干

优先顺序：

1. 先看高层 fuser 组件
2. 再看 `OneFuser`
3. 只有 `fuser` 不适用时，再继续看 transformer / attention

补充约束：

- 若 `fuser` 契约已能覆盖主干需求，默认不要直接从底层 transformer block 手工拼 encoder/decoder 作为首选实现
- 若需要回到底层 block，应先在规格中说明当前 `fuser` 为什么不适用

### sample

适用于：

- 下采样
- 上采样
- 特征分辨率调整
- U 形主干中的尺度变换

优先顺序：

1. 先看具体 downsample / upsample 组件
2. 再看 `OneSample`

### recovery

适用于：

- patch 级输出恢复
- token 到物理场的输出投影
- 2D / 3D 特征恢复到目标变量网格

优先顺序：

1. 先看具体 recovery 组件
2. 再看 `OneRecovery`

### encoder / decoder

适用于：

- 明确的编码器分支
- 明确的解码器分支
- 多分支结构中的局部表征抽取与恢复

优先顺序：

1. 先看具体 encoder / decoder 组件
2. 再看 `OneEncoder` / `OneDecoder`

### transformer / attention / afno / fc

适用于：

- 高层组件无法覆盖时的继续下钻
- 对 block 级或算子级实现进行替换
- 明确需要底层算子能力时

优先顺序：

1. 先看高层组件
2. 再看对应 `One*` 入口
3. 最后看底层模块

### mlp / fourier / head

适用于：

- 神经算子前的点级或 token 级特征映射
- `FNO / U_FNO / U_NO` 这类谱域主干
- `U_Net` 多尺度主干后的输出投影

优先顺序：

1. 先看模型卡，确认具体依赖的是哪一个 wrapper
2. 再看 `OneMlp` / `OneFourier` / `OneHead`
3. 只有 wrapper 契约仍不足时，再回到对应底层实现

### pooling / processor / edge / node

适用于：

- MeshGraphNet / BSMS-MGN 这类显式图结构模型
- GraphViT 这类节点到 cluster token 再回到节点的流程
- 非结构网格、粒子、点云流场任务中的 message passing
- 需要多尺度图处理或层级图 U-Net 的 CFD 任务

优先顺序：

1. 先看模型卡，确认当前案例使用的是 GraphViT、MeshGraphNet 还是 BiStrideMeshGraphNet
2. 若是标准 MeshGraphNet message passing，先看 `OneEdge` / `OneNode`
3. 若是多尺度 BSMS-MGN，先看 `OneProcessor`
4. 若是 GraphViT 的 cluster 压缩，先看 `OnePooling`
5. 若 datapipe 尚未提供边、cluster、mask 或多尺度索引，优先补数据接口，不要直接改模型 block

### equivariant

适用于：

- GFNO 等 group-equivariant neural operator
- 需要旋转或反射等变卷积 stem 的结构化网格任务
- 与 `GSpectralConv*d`、`GroupEquivariantMLP*d` 成套使用的算子主干

优先顺序：

1. 先确认模型目标是否确实是 GFNO 或等变神经算子
2. 再看 `OneEquivariant`
3. 同时核对 `OneFourier` 中的 `GSpectralConv*d` 和 `OneMlp` 中的 `GroupEquivariantMLP*d`
4. 如果只是普通 FNO / U-FNO 对比，不要默认启用等变组件

## 典型检索顺序

对于天气预测、全球格点预报、surface 与 upper-air 联合建模这类任务，推荐优先顺序：

1. `embedding`
2. `fuser`
3. `sample`
4. `recovery`

对于 CFD 代理、神经算子、非结构网格和图网络任务，推荐优先顺序：

1. 先看 `../models/model_index.md` 和最接近的模型卡
2. 规则网格任务优先检查 `encoder / decoder / head` 或 `mlp / fourier`
3. 非结构点云转规则潜网格任务优先检查 `mlp / fourier`，特别是 `GeoSpectralConv*d`
4. 显式图任务优先检查 `mlp / edge / node / processor / pooling`
5. 等变神经算子任务优先检查 `equivariant / fourier / mlp`

在某个模块族内部，再根据以下条件筛选：

- 输入输出 shape 是否匹配
- 是否支持当前任务需要的 2D / 3D 形态
- 调用入口与注册名是否明确
- 契约卡片是否已覆盖当前任务关键参数
- 是否已有相近模型或案例可以参考

## 继续下钻的规则

若上层组件卡片中已经写明“内部依赖某个 block / attention / afno / fc / wrapper”，建议按下面顺序继续下钻：

1. 先看该高层组件自己的契约卡
2. 再看对应 `One*` 入口卡
3. 再看下层 block / attention / afno / fc 卡
4. 只有契约仍不足时，再回到源码

## 建议维护规则

新增组件时，建议至少补以下字段：

- 组件名
- 所属模块族
- 调用入口
- 注册名
- 输入形态摘要
- 当前状态
- 契约卡片

推荐状态值：

- `stable`
- `in_progress`
- `legacy_split`

推荐新增流程：

1. 先复制 `./TEMPLATE.md`
2. 按组件实际情况填写字段
3. 将新契约文件加入本索引
4. 若该组件已经替代旧实现，在风险点中明确说明

## 相关文档

- `./TEMPLATE.md`
- `./naming_convention.md`

## 检索约定

源码锚点统一使用 `./onescience/...` 相对路径。

默认假设：

- ``
- `onescience/`

位于同一工作目录下。
