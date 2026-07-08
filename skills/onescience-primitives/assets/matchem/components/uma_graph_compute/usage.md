# launch
Python API 示例：

``` python
import torch
from onescience.modules.func_utils.uma_graph.compute import generate_graph

graph = generate_graph(
    data=batch,
    cutoff=6.0,
    max_neighbors=50,
    enforce_max_neighbors_strictly=True,
    radius_pbc_version=2,
    pbc=torch.tensor([[True, True, True]], device=batch.pos.device),
)
```

完整 UMA 推理/训练中通过图配置控制：

``` sh
python examples/matchem/uma/train.py --config-name=uma_finetune --model.backbone.otf_graph=true --model.backbone.cutoff=6.0 --model.backbone.max_neighbors=50 --model.backbone.enforce_max_neighbors_strictly=true --model.backbone.radius_pbc_version=2 --trainer.max_epochs=10 --optim.batch_size=2
```

# input_schema
输入准备流程：

结构 batch
  pos: (NumAtoms, 3)
  cell: (NumGraphs, 3, 3)
  natoms: (NumGraphs,)
  pbc: (NumGraphs, 3)

邻居搜索参数
  cutoff
  max_neighbors
  enforce_max_neighbors_strictly
  radius_pbc_version

逐结构构图
  data[idx]
    -> radius_graph_pbc / radius_graph_pbc_v2
    -> edge_index_per_system
    -> cell_offsets_per_system
    -> neighbors_per_system

batch 合并
  atom_index_offset = cumsum(natoms)
    -> edge_index: (2, NumEdges)
    -> get_pbc_distances
    -> edge_distance / edge_distance_vec / offsets

# runtime_interfaces
- `generate_graph(data, cutoff, max_neighbors, enforce_max_neighbors_strictly, radius_pbc_version, pbc)`：生成 UMA 图字段。
- `get_pbc_distances(pos, edge_index, cell, cell_offsets, neighbors, return_offsets=False, return_distance_vec=False)`：根据 cell offsets 修正周期距离并过滤零距离边。

# main_functions
- `generate_graph`
- `get_pbc_distances`

# execution_resources
- 构图成本随 `NumAtoms`、cutoff、`max_neighbors` 和 batch size 增长。
- 大 cutoff 或宽松 neighbor 上限会显著增加边数和后续 backbone 显存。
- `generate_graph` 当前禁用 torch compiler 内部编译，适合作为运行时工具而非编译优化热点。
- CPU/GPU 执行取决于 batch tensor 所在 device 和 radius graph 实现。

# operation_limits
- `radius_pbc_version` 只能为 `1` 或 `2`。
- PBC 体系需要有效非零 cell。
- 混合周期和非周期体系需明确 pbc 策略。
- `get_pbc_distances` 会过滤距离为 0 的边，边数可能少于 radius graph 初始输出。
- 外部图输入模式必须提供完整且同源的边字段。
