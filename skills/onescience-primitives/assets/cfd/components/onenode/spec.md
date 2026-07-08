# component_info
OneNode 位于 node 模块，是 MeshGraphNet 类 processor 中的节点状态更新原语，负责聚合邻接边消息并更新节点隐状态。

# purpose
- 做什么：根据边消息和当前节点表征更新节点状态。
- 解决问题：统一调用 MeshNodeBlock。
- 适用场景：非结构网格 CFD、图代理模型、粒子状态更新。
- 不适用场景：无显式图拓扑的规则网格卷积。

# input_schema
典型输入为 `edge_features, node_features, graph`；graph 中的边方向决定消息聚合到哪个节点。

# output_schema
通常返回更新后的节点特征或底层 block 约定的 `(edge_features, node_features)` 结构；节点最后一维多为 `output_dim`。

# parameters
- `style`：注册表名称，常见取值包括 `MeshNodeBlock`。
- `**kwargs`：透传给目标 节点更新 实现。
- 常见参数：`aggregation`、`input_dim_nodes`、`input_dim_edges`、`output_dim`、`hidden_dim`、`hidden_layers`、`norm_type`、`activation_fn`。

# key_dependencies
- _lazy.py
- mesh_node_block.py

# usage_and_risks
- `aggregation` 会影响数值尺度和 rollout 稳定性。
- graph、edge_features、node_features 必须同序。
- 不负责边界条件 mask 或构图。
- 节点目标维度与最终物理变量维度不一定相同。

# code_references
- `{onescience_path}/onescience/src/onescience/modules/node/onenode.py`
- `{onescience_path}/onescience/src/onescience/modules/node/mesh_node_block.py`
- `{onescience_path}/onescience/src/onescience/models/meshgraphnet/meshgraphnet.py`
