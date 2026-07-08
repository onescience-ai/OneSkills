# component_info
OneMlp 位于 mlp 模块，是特征升维、通道混合、节点/边编码和轻量输出投影的统一入口。

# purpose
- 做什么：对点、token、节点、边或通道特征做非线性映射。
- 解决问题：统一管理 StandardMLP、MeshGraphMLP 和 GroupEquivariantMLP。
- 适用场景：输入 lifting、processor 内部 FFN、图节点/边 encoder/decoder、GFNO channel mixing。
- 不适用场景：需要空间卷积、频域卷积或显式注意力的阶段。

# input_schema
StandardMLP 通常接收 `(..., FeatureDim)`；MeshGraphMLP 接收节点/边特征；GroupEquivariantMLP*d 通常接收等变通道布局的网格张量。

# output_schema
StandardMLP 输出 `(..., output_dim)`；图 MLP 输出节点/边目标维度；等变 MLP 保持空间维并映射通道。

# parameters
- `style`：注册表名称，常见取值包括 `StandardMLP`, `MeshGraphMLP`, `GroupEquivariantMLP2d`, `XiheMlp`。
- `**kwargs`：透传给目标 MLP 实现。
- StandardMLP 常用 `input_dim`、`hidden_dims`、`output_dim`、`activation`。
- MeshGraphMLP 常用 `input_dim`、`output_dim`、`hidden_dim`、`hidden_layers`、`norm_type`。
- GroupEquivariantMLP 使用 `in_channels/out_channels/mid_channels` 等通道参数。

# key_dependencies
- _lazy.py
- MLP.py
- mesh_graph_mlp.py
- GMLP.py
- xihemlp.py

# usage_and_risks
- 不同 MLP style 参数名不同。
- channel-first 张量不能直接当作 `(..., FeatureDim)` 输入 StandardMLP。
- 图 MLP 的 LayerNorm 和 residual 约定会影响 rollout 稳定性。
- style 未注册或 kwargs 冲突会失败。

# code_references
- `{onescience_path}/onescience/src/onescience/modules/mlp/onemlp.py`
- `{onescience_path}/onescience/src/onescience/modules/mlp/MLP.py`
- `{onescience_path}/onescience/src/onescience/modules/mlp/mesh_graph_mlp.py`
- `{onescience_path}/onescience/src/onescience/modules/mlp/GMLP.py`
