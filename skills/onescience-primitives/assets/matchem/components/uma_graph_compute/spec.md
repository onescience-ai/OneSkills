# component_info
`uma_graph_compute` 是 UMA func_utils 中的图构建组件，定位为从原子坐标和晶胞生成 eSCNMD backbone 所需边几何字段。它通过直接导入调用，核心特征是支持 PBC 半径图、邻居数限制、batch 合并和边距离向量输出。

# purpose
- 用途：构造 UMA 原子近邻图，计算 PBC 距离、cell offsets、边向量和邻居计数。
- 解决问题：把结构 batch 的坐标与晶胞转换成 backbone 可消费的边字段。
- 适用场景：UMA on-the-fly graph、calculator 推理、fine-tuning、非外部图输入。
- 不适用场景：网络消息传递、loss、head 输出、径向 MLP 本身。

# input_schema
- `data`: batch 对象或 dict-like 结构，包含 `pos`、`cell`、`natoms`，并可按结构索引。
- `pos`: `(NumAtoms, 3)`。
- `cell`: `(NumGraphs, 3, 3)`。
- `natoms`: `(NumGraphs,)`。
- `cutoff`: 邻居搜索半径。
- `max_neighbors`: 每原子最大邻居数。
- `enforce_max_neighbors_strictly`: 是否严格限制邻居数。
- `radius_pbc_version`: `1` 或 `2`。
- `pbc`: `(NumGraphs, 3)` 或逐结构周期布尔信息。

# output_schema
- `edge_index`: `(2, NumEdges)`。
- `edge_distance`: `(NumEdges,)`。
- `edge_distance_vec`: `(NumEdges, 3)`。
- `cell_offsets`: `(NumEdges, 3)`。
- `offset_distances`: `(NumEdges, 3)`，由 cell offsets 转换后的实际偏移向量。
- `neighbors`: per-image 或 per-atom 邻居计数，来自 radius graph 实现。
- `get_pbc_distances` 可选返回 `offsets` 和 `distance_vec`。

# parameters
- `cutoff`: 邻居截断半径。
- `max_neighbors`: 最大邻居数。
- `enforce_max_neighbors_strictly`: 是否严格裁剪邻居。
- `radius_pbc_version`: 选择 `radius_graph_pbc` 或 `radius_graph_pbc_v2`。
- `pbc`: 周期边界条件。
- `return_offsets`: 是否返回 offset 向量。
- `return_distance_vec`: 是否返回边距离向量。
- `otf_graph`: 配置层常见开关，决定是否运行时构图。
- `always_use_pbc`: 配置层常见策略，决定非周期体系如何处理。

# key_dependencies
- `radius_graph_pbc.py`
- `uma_radial.py`
- `uma_escn_md.py`
- `uma_calculator.py`

# usage_and_risks
- 典型使用：`eSCNMDBackbone.forward` 或 calculator 在缺少外部边字段时调用 `generate_graph`。
- 改 `max_neighbors` 或 cutoff 会改变边数、显存和模型感受野。
- 混合 PBC batch、zero cell 或错误 pbc 字段可能导致构图失败。
- `otf_graph=False` 时必须由外部提供完整 `edge_index`、`edge_distance`、`edge_distance_vec` 等字段。
- 训练和推理构图策略不同会造成不可解释误差。

# code_references
- `{onescience_path}/onescience/src/onescience/modules/func_utils/uma_graph/compute.py`
- `{onescience_path}/onescience/src/onescience/modules/func_utils/uma_graph/radius_graph_pbc.py`
- `{onescience_path}/onescience/src/onescience/models/UMA/uma_escn_md.py`
