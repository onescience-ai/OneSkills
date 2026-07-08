# component_info
OneEdge 位于 edge 模块，是 MeshGraphNet 类 processor 中的边消息更新原语，负责基于相邻节点与边属性更新边隐状态。

# purpose
- 做什么：更新图边表征。
- 解决问题：把 MeshGraphNet 的边更新 block 纳入统一注册入口。
- 适用场景：非结构网格 CFD、粒子系统、显式图 message passing。
- 不适用场景：无边拓扑的规则 CNN/FNO 网格。

# input_schema
典型输入为 `edge_features, node_features, graph`，其中边数量和顺序必须与 graph 内部边顺序一致。

# output_schema
通常返回更新后的边特征以及底层 block 约定的附加结构；最后一维多为 `output_dim`。

# parameters
- `style`：注册表名称，常见取值包括 `MeshEdgeBlock`。
- `**kwargs`：透传给目标 边更新 实现。
- 常见参数：`input_dim_nodes`、`input_dim_edges`、`output_dim`、`hidden_dim`、`hidden_layers`、`aggregation`、`norm_type`、`activation_fn`。

# key_dependencies
- _lazy.py
- mesh_edge_block.py

# usage_and_risks
- 不负责构图或补边。
- graph 必须兼容底层 MeshEdgeBlock。
- 节点/边特征维度不可混用。
- 边方向和顺序错误会造成静默语义错误。

# code_references
- `{onescience_path}/onescience/src/onescience/modules/edge/oneedge.py`
- `{onescience_path}/onescience/src/onescience/modules/edge/mesh_edge_block.py`
- `{onescience_path}/onescience/src/onescience/models/meshgraphnet/meshgraphnet.py`
