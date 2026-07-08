# component_info
`mace_func_utils` 是 MACE func_utils 族中的图准备、物理导数和训练统计组件，定位为模型 forward 与训练流程之间的运行工具层。它不定义网络参数，而是把原子图几何、能量张量和 batch 结构转换为 forces、virials、stress、Hessian 与统计量。

# purpose
- 用途：准备 MACE 图上下文，计算边几何，基于能量自动微分生成力、virial、stress、Hessian 和边力。
- 解决问题：保证能量守恒势函数的物理量输出与 autograd 路径一致，并提供训练前统计量。
- 适用场景：MACE/ScaleShiftMACE forward、calculator 推理、MD、训练数据统计、LAMMPS/MLIAP 分支。
- 不适用场景：定义 neural block、读取 extxyz、计算训练 loss、选择模型超参。

# input_schema
- `positions`: `(NumAtoms, 3)`，需要求力时必须保留梯度。
- `cell`: `(NumGraphs, 3, 3)` 或等价 cell，周期体系和 stress/virial 需要。
- `edge_index`: `(2, NumEdges)`。
- `shifts` / `unit_shifts`: `(NumEdges, 3)`，PBC 边偏移。
- `batch`: `(NumAtoms,)`。
- `energy`: 图级能量张量。
- `training`: 是否以训练模式创建导数图。
- `lammps_mliap`: LAMMPS 兼容分支开关。
- `fixed_fields`: 固定外场或不参与导数的字段集合。

# output_schema
- `GraphContext`: 包含图几何、节点 head、batch 和 displacement 等 forward 上下文。
- `InteractionKwargs`: 传给 interaction block 的几何与 head 参数集合。
- `edge_vectors`: `(NumEdges, 3)`。
- `lengths`: `(NumEdges,)`。
- `forces`: `(NumAtoms, 3)`。
- `virials`: `(NumGraphs, 3, 3)`。
- `stress`: `(NumGraphs, 3, 3)`。
- `hessian`: 可选二阶导，计算成本高。
- `atomic_virials` / `atomic_stresses`: 可选逐原子张量。
- `avg_num_neighbors`、mean/std、rms forces、rms dipoles 等统计量。

# parameters
- `compute_force`: 是否从能量求力。
- `compute_virials`: 是否计算 virial。
- `compute_stress`: 是否计算 stress。
- `compute_hessian`: 是否计算 Hessian。
- `compute_edge_forces`: 是否计算边力。
- `compute_atomic_stresses`: 是否计算逐原子 stress。
- `compute_displacement`: 是否构造晶胞扰动。
- `training`: 是否保留高阶梯度图。
- `lammps_mliap`: 是否启用 LAMMPS/MLIAP 特殊处理。
- `fixed_fields`: 控制哪些输入字段固定。

# key_dependencies
- `mace_block.py`
- `mace_loss.py`
- `mace_irreps_tools.py`
- `scatter.py`
- `torch_geometric.batch.py`
- `mace.py`

# usage_and_risks
- 典型使用：由 `MACE.forward` 调用 `prepare_graph` 和 `get_outputs`，训练前调用 `compute_statistics` 或 `compute_avg_num_neighbors`。
- `positions` 被 detach、拷贝或未设置梯度会导致 forces 为 `None` 或错误。
- `cell`、`shifts` 和 `unit_shifts` 不一致会污染 PBC 导数。
- stress 单位和符号依赖体积与数据来源，必须与 loss 和指标保持一致。
- Hessian、逐原子 stress 和边力成本高，不应默认开启。
- LAMMPS 分支会改变节点切片语义，需要单独测试。

# code_references
- `{onescience_path}/onescience/src/onescience/modules/func_utils/mace_func_utils.py`
- `{onescience_path}/onescience/src/onescience/modules/func_utils/mace_irreps_tools.py`
- `{onescience_path}/onescience/src/onescience/models/mace/mace.py`
