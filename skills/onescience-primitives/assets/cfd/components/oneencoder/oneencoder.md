# Contract: OneEncoder

## 基本信息

- 组件名：`OneEncoder`
- 所属模块族：`encoder`
- 统一入口：`OneEncoder`
- 注册名：`style="OneEncoder"`

## 组件说明
OneEncoder 位于 encoder 模块，是把原始网格场、图结构、天气 token 或生物结构特征转成模型隐表征的统一入口。它保留底层 encoder 的接口语义，并额外提供 state_dict 前缀适配逻辑。

## 用途
- 做什么：统一调度多种 encoder 实现。
- 解决问题：将规则网格、图、天气 token、Protenix atom/pair 条件编码纳入同一构造模式。
- 适用场景：模型输入特征升维、U-Net skip 编码、GraphViT/MeshGraph 编码、FengWu 编码。
- 不适用场景：数据读取、归一化、构图或坐标预处理。

## 输入规格
按 style 准备输入：

UNetEncoder*d
  x: (Batch, Channels, ...Spatial)

GraphViTEncoder
  mesh_pos、edges、states、node_type、pos_enc

MeshGraphEncoder
  node_features、edge_features、graph

FengWu/Protenix
  由对应主模型定义的 token、pair 或 atom 输入

## 输出规格
UNet encoder 通常返回多尺度 feature/skip 列表；Graph/Mesh encoder 返回节点和边隐表征；FengWu/Protenix 分支返回对应模型内部表征。OneEncoder 不重排、不拆包。

## 参数
- `style`：`UNetEncoder1D/2D/3D`、`GraphViTEncoder`、`MeshGraphEncoder`、`FengWuEncoder`、`ProtenixRelativePositionEncoding`、`ProtenixAtomAttentionEncoder`。
- `**kwargs`：底层 encoder 参数，如 `in_channels`、`base_channels`、`num_stages`、`normtype`、`state_size`、隐藏维度等。
- `load_state_dict(strict=True)`：会为传入权重键添加 `encoder.` 前缀，适合加载裸 encoder 权重。

## 关键依赖
- _lazy.py
- unet_encoder.py
- graphvit_encoder.py
- mesh_graph_encoder.py
- fengwuencoder.py
- protenixencoding.py

## 使用注意与风险
- wrapper 无法判断输入是 grid、token 还是 graph。
- UNet encoder 输出的 skip 顺序必须与 decoder 匹配。
- GraphViT/MeshGraph 依赖拓扑、节点顺序和位置编码。
- Protenix encoder 不是通用图节点编码器。

## 启动方式
Python API 启动，调用方按目标 style 传入底层实现参数：

``` sh
python -c "from onescience.modules.encoder.oneencoder import OneEncoder; m=OneEncoder(style='UNetEncoder2D'); print(type(m).__name__)"
```

在模型 pipeline 中通常由上层模型构造函数实例化，不单独提供 CLI。

## 输入规格
从 datapipe 输出中整理字段：规则场按 channel-first 张量组织；图数据需提供节点、边和 graph；GraphViT 还需 cluster/位置编码；Protenix 由模型特征构造器提供。

## 运行接口
- 构造接口：`OneEncoder(style, **kwargs)`。
- 调用接口：`encoder(*args, **kwargs)`。
- 权重接口：`load_state_dict(state_dict, strict=True)` 对裸 encoder 权重键加前缀。
- 属性访问：未命中的属性转发到底层 encoder。

## 主要函数
- `forward`

## 执行资源
规则网格 encoder 消耗随分辨率和通道数增长；图 encoder 消耗随节点/边数增长；通常建议在 GPU 上训练，轻量 shape 检查可在 CPU 上完成。

## 操作限制
不做数据格式转换、不构图、不创建位置编码；不同 encoder 的输出不能默认互换。

## 规划决策

### 描述
OneEncoder 是输入进入模型主干前的表示转换阶段，规划时先判定数据拓扑，再选择 encoder family。

### 使用时机
需要通过统一配置切换不同编码器，或上层模型希望隐藏底层 encoder import 路径时使用。

### 输入
- 数据形态：规则网格、点云、显式图、天气 token 或 atom/pair 特征。
- 目标隐维度与下游 decoder/trunk 需求。
- 是否需要多尺度 skip。
- 是否已有位置编码、边特征和 graph。

### 输出
- encoder style 与参数。
- 输入字段映射。
- 输出结构说明。
- 与 transformer/decoder 的 shape 契约。

### 执行步骤
1. 判断数据拓扑和空间维度。
2. 选择 encoder family。
3. 让 datapipe 输出字段与 forward 签名对齐。
4. 实例化并跑一批 shape 检查。
5. 将输出结构传给后续 trunk/decoder 规划。

### 约束
encoder 与 decoder/trunk 必须在隐藏维度和结构语义上匹配；Graph family 必须具备有效拓扑。

### 下一阶段建议
补充 encoder-to-decoder 的最小联调样例，记录 skip、节点和边表征的命名约定。

### 回退策略
若输入不是目标 encoder 支持的形态，先增加预处理或改用更匹配的 encoder；若权重加载失败，检查是否需要裸权重前缀适配。

## 源码锚点

- `{onescience_path}/onescience/src/onescience/modules/encoder/oneencoder.py`
- `{onescience_path}/onescience/src/onescience/modules/encoder/fengwuencoder.py`
- `{onescience_path}/onescience/src/onescience/modules/encoder/unet_encoder.py`
- `{onescience_path}/onescience/src/onescience/modules/encoder/graphvit_encoder.py`
- `{onescience_path}/onescience/src/onescience/modules/encoder/protenixencoding.py`
