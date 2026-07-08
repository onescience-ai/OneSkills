# component_info
`uma_embedding` 是 UMA embedding 族组件，定位为 eSCNMD backbone 的输入条件与边度初始化层。它将原子图中的边距离、原子编号、charge、spin 和 dataset 信息编码成节点球谐特征或条件向量，为后续等变 block 和多数据集任务提供上下文。

# purpose
- 用途：构造 UMA 的 edge degree embedding、charge/spin embedding 和 dataset embedding。
- 解决问题：让 backbone 在开始消息传递前获得局部连通性、系统电荷自旋和数据集条件。
- 适用场景：UMA backbone 初始化、多数据集训练、charge/spin 条件模型、MoE 路由辅助。
- 不适用场景：输出 head、loss、近邻图搜索、stress/force 导数计算。

# input_schema
- `atomic_numbers`: `(NumAtoms,)`。
- `edge_index`: `(2, NumEdges)`。
- `edge_distance`: `(NumEdges,)`。
- `edge_distance_vec`: `(NumEdges, 3)`。
- `batch`: `(NumAtoms,)`。
- `charge`: `(NumGraphs,)` 或 batch 字段。
- `spin`: `(NumGraphs,)` 或 batch 字段。
- `dataset`: dataset name / id 列表。
- Wigner / SO3 mapping 相关对象：edge degree embedding 需要。

# output_schema
- `EdgeDegreeEmbedding`: 与节点球谐特征同形态或可加到节点特征的张量。
- `ChgSpinEmbedding`: 系统级 charge/spin 条件向量，可广播到节点或图级分支。
- `DatasetEmbedding`: 数据集条件向量，用于多数据集 head、normalizer 或 MoE 路由。

# parameters
- `sphere_channels`: 球谐通道数。
- `lmax`: 最大角动量。
- `mmax`: 最大 m 阶。
- `edge_channels_list`: 边径向通道配置。
- `cutoff`: 边距离截断。
- `rescale_factor`: 边度嵌入缩放。
- `embedding_type`: 条件嵌入类型。
- `embedding_target`: 条件嵌入目标位置。
- `dataset_list`: 支持的数据集列表。
- `embedding_size`: dataset 或 charge/spin embedding 大小。

# key_dependencies
- `uma_radial.py`
- `uma_escn_md_block.py`
- `uma_moe.py`
- `uma_head.py`
- `uma_escn_md.py`
- `uma_escn_moe.py`

# usage_and_risks
- 典型使用：由 `eSCNMDBackbone` 或 `eSCNMDMoeBackbone` 在 forward 早期构造初始节点表示与条件向量。
- 新增 dataset 时，需要同步扩展 `dataset_list`、head wrapper、normalizer 和 task 配置。
- charge/spin 字段缺失时不能随意填充，需要确认预训练模型是否依赖该条件。
- edge 通道改变会影响径向 MLP、block 线性层和 checkpoint 加载。
- dataset embedding、head wrapper、normalizer 必须同源，否则多数据集任务会错配。

# code_references
- `{onescience_path}/onescience/src/onescience/modules/embedding/uma_embedding.py`
- `{onescience_path}/onescience/src/onescience/models/UMA/uma_escn_md.py`
- `{onescience_path}/onescience/src/onescience/models/UMA/uma_escn_moe.py`
