# component_info
OneEncoder 位于 encoder 模块，是把原始网格场、图结构、天气 token 或生物结构特征转成模型隐表征的统一入口。它保留底层 encoder 的接口语义，并额外提供 state_dict 前缀适配逻辑。

# purpose
- 做什么：统一调度多种 encoder 实现。
- 解决问题：将规则网格、图、天气 token、Protenix atom/pair 条件编码纳入同一构造模式。
- 适用场景：模型输入特征升维、U-Net skip 编码、GraphViT/MeshGraph 编码、FengWu 编码。
- 不适用场景：数据读取、归一化、构图或坐标预处理。

# input_schema
按 style 准备输入：

UNetEncoder*d
  x: (Batch, Channels, ...Spatial)

GraphViTEncoder
  mesh_pos、edges、states、node_type、pos_enc

MeshGraphEncoder
  node_features、edge_features、graph

FengWu/Protenix
  由对应主模型定义的 token、pair 或 atom 输入

# output_schema
UNet encoder 通常返回多尺度 feature/skip 列表；Graph/Mesh encoder 返回节点和边隐表征；FengWu/Protenix 分支返回对应模型内部表征。OneEncoder 不重排、不拆包。

# parameters
- `style`：`UNetEncoder1D/2D/3D`、`GraphViTEncoder`、`MeshGraphEncoder`、`FengWuEncoder`、`ProtenixRelativePositionEncoding`、`ProtenixAtomAttentionEncoder`。
- `**kwargs`：底层 encoder 参数，如 `in_channels`、`base_channels`、`num_stages`、`normtype`、`state_size`、隐藏维度等。
- `load_state_dict(strict=True)`：会为传入权重键添加 `encoder.` 前缀，适合加载裸 encoder 权重。

# key_dependencies
- _lazy.py
- unet_encoder.py
- graphvit_encoder.py
- mesh_graph_encoder.py
- fengwuencoder.py
- protenixencoding.py

# usage_and_risks
- wrapper 无法判断输入是 grid、token 还是 graph。
- UNet encoder 输出的 skip 顺序必须与 decoder 匹配。
- GraphViT/MeshGraph 依赖拓扑、节点顺序和位置编码。
- Protenix encoder 不是通用图节点编码器。

# code_references
- `{onescience_path}/onescience/src/onescience/modules/encoder/oneencoder.py`
- `{onescience_path}/onescience/src/onescience/modules/encoder/fengwuencoder.py`
- `{onescience_path}/onescience/src/onescience/modules/encoder/unet_encoder.py`
- `{onescience_path}/onescience/src/onescience/modules/encoder/graphvit_encoder.py`
- `{onescience_path}/onescience/src/onescience/modules/encoder/protenixencoding.py`
