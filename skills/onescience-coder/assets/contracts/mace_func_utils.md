# Contract: mace_func_utils.py

## 基本信息

- 组件名：`MACE Autograd and Graph Utilities`
- 所属模块族：`materials / mace / func_utils`
- 统一入口：`direct_import`
- 注册名：`not_applicable`
- 主源码：`./onescience/src/onescience/modules/func_utils/mace_func_utils.py`

## 组件职责

提供 MACE 模型输出链路中的图准备、边向量计算、能量导数、统计量计算和不变量抽取。

关键函数：

- `prepare_graph`
- `get_edge_vectors_and_lengths`
- `get_outputs`
- `compute_forces`
- `compute_forces_virials`
- `get_symmetric_displacement`
- `compute_hessians_vmap` / `compute_hessians_loop`
- `get_atomic_virials_stresses`
- `compute_statistics`
- `compute_avg_num_neighbors`

## 输入契约

- `positions`: `(NumAtoms, 3)`，需要求力时必须保留梯度
- `cell`: `(NumGraphs, 3, 3)` 或等价 cell
- `edge_index`: `(2, NumEdges)`
- `shifts` / `unit_shifts`: PBC 边偏移
- `batch`: `(NumAtoms,)`
- `energy`: 图级能量张量

## 输出契约

- `forces`: `(NumAtoms, 3)`
- `virials`: `(NumGraphs, 3, 3)`
- `stress`: `(NumGraphs, 3, 3)`
- `hessian`: 可选二阶导
- `edge_vectors` / `lengths`: 构图后边几何量
- `avg_num_neighbors`、mean/std、rms forces 等训练统计量

## 关键参数

- `compute_force`
- `compute_virials`
- `compute_stress`
- `compute_hessian`
- `training`
- `lammps_mliap`
- `fixed_fields`

## 典型调用位置

- `MACE.forward`
- `ScaleShiftMACE.forward`
- `AtomicDipolesMACE` / `EnergyDipolesMACE`
- 训练前统计量计算
- calculator 推理与 MD

## 常见修改点

- 增加新导数量：先确认 energy 对目标变量存在 autograd 路径。
- 改 stress/virial：同时确认 symmetric displacement 和 cell 梯度。
- 处理 LAMMPS：保持 `prepare_graph` 中 ghost atom 和 batch 语义。
- 性能优化：优先减少不必要的 Hessian/virial 计算。

## 风险点

- `positions` 被 detach 或复制后会导致 forces 为 None 或错误。
- `cell` 和 `shifts` 不一致会导致 PBC force/stress 异常。
- stress 单位通常依赖体积换算，必须和数据来源校准。
- Hessian 计算成本高，不应默认开启。

## 下钻关系

- MACE block 输出：`./mace_block.md`
- loss 消费字段：`./mace_loss.md`
- calculator：`./mace_calculator.md`
- 数据构图：`../datapipes/materials_mace.md`

## 源码锚点

- `./onescience/src/onescience/modules/func_utils/mace_func_utils.py`
- `./onescience/src/onescience/modules/func_utils/mace_irreps_tools.py`
- `./onescience/src/onescience/models/mace/mace.py`
