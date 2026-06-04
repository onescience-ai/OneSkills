# Contract: uma_graph_compute.py

## 基本信息

- 组件名：`UMA Graph Compute`
- 所属模块族：`materials / uma / func_utils`
- 统一入口：`direct_import`
- 注册名：`not_applicable`
- 主源码：`./onescience/src/onescience/modules/func_utils/uma_graph/compute.py`

## 组件职责

构造 UMA 所需的原子近邻图，计算 PBC 距离、cell offsets、边向量和邻接关系。

覆盖函数：

- `generate_graph`
- `get_pbc_distances`
- `radius_graph_pbc` 下游实现

## 输入契约

- `pos`: `(NumAtoms, 3)`
- `cell`: `(NumGraphs, 3, 3)`
- `natoms`: `(NumGraphs,)`
- `pbc`: 周期边界布尔信息
- `cutoff`
- `max_neighbors`
- `otf_graph`

## 输出契约

- `edge_index`: `(2, NumEdges)`
- `edge_distance`: `(NumEdges,)`
- `edge_distance_vec`: `(NumEdges, 3)`
- `cell_offsets`: `(NumEdges, 3)`
- `neighbors`: per-image neighbor count

## 关键参数

- `cutoff`
- `max_neighbors`
- `enforce_max_neighbors_strictly`
- `radius_pbc_version`
- `always_use_pbc`
- `otf_graph`

## 典型调用位置

- `eSCNMDBackbone.forward`
- `FAIRChemCalculator`
- UMA inference scripts
- UMA Hydra fine-tuning

## 常见修改点

- 改 neighbor 策略：同步检查 `max_neighbors`、cutoff 和显存。
- 处理非周期分子：确认 `always_use_pbc`、zero cell 和 pbc 字段。
- 外部 graph 输入：`otf_graph=False` 时必须提供完整边字段。

## 风险点

- 混合 PBC batch 可能触发 calculator 或图构建错误。
- zero cell 用于周期体系会导致图构建失败。
- `max_neighbors` 太小会截断关键相互作用，太大则显存不可控。
- 推理和训练的 graph 策略不同会带来不可解释误差。

## 源码锚点

- `./onescience/src/onescience/modules/func_utils/uma_graph/compute.py`
- `./onescience/src/onescience/modules/func_utils/uma_graph/radius_graph_pbc.py`
- `./onescience/src/onescience/models/UMA/uma_escn_md.py`

## 下钻关系

- 径向边特征：`./uma_radial.md`
- calculator：`./uma_calculator.md`
- 数据字段：`../datapipes/materials_uma.md`
