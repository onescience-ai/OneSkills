# component_info
`mesh_graph_mlp` 属于 `mlp` 模块族，核心实现类/函数包括 `CustomSiLuLinearAutogradFunction`、`MeshGraphMLP`、`MeshGraphEdgeMLPConcat`、`MeshGraphEdgeMLPSum`。它的定位是图 MLP 模块，由上层 OneScience 模型或流水线通过 Python API 调用。

# purpose
以多层感知机形式变换图节点或边特征，适用于 GraphCast 消息传递模块。

# input_schema
- 图节点特征：`(N_nodes, feature_dim)`
- 图边特征：`(N_edges, feature_dim)`
- 图结构：DGL 图或等价的源/目标索引关系。

# output_schema
- 输出为更新后的节点特征、边特征或嵌入特征，维度由 `output_dim`、`hidden_dim` 等参数控制。

# parameters
- `MeshGraphMLP` 构造参数：`input_dim`, `output_dim`, `hidden_dim`, `hidden_layers`, `activation_fn`, `norm_type`, `recompute_activation`
- `MeshGraphEdgeMLPConcat` 构造参数：`efeat_dim`, `src_dim`, `dst_dim`, `output_dim`, `hidden_dim`, `hidden_layers`, `activation_fn`, `norm_type`, `bias`, `recompute_activation`
- `MeshGraphEdgeMLPSum` 构造参数：`efeat_dim`, `src_dim`, `dst_dim`, `output_dim`, `hidden_dim`, `hidden_layers`, `activation_fn`, `norm_type`, `bias`, `recompute_activation`

# key_dependencies
- `gnnlayer_utils`

# usage_and_risks
- 输入张量维度必须与构造参数中的通道数、网格分辨率、patch 大小或图特征维度一致。
- 该组件通常依赖上层模型完成数据标准化、变量排序和设备迁移，单独调用时需显式准备。
- 图结构、节点顺序和边特征语义必须在 encoder、processor、decoder 阶段保持一致。

# code_references
- `{onescience_path}/onescience/src/onescience/modules/mlp/mesh_graph_mlp.py`
