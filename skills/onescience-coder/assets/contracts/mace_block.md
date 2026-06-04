# Contract: mace_block.py

## 基本信息

- 组件名：`MACE Block Family`
- 所属模块族：`materials / mace / block`
- 统一入口：`direct_import`
- 注册名：`not_applicable`
- 主源码：`./onescience/src/onescience/modules/block/mace_block.py`

## 组件职责

提供 MACE 主干的核心积木：节点嵌入、径向嵌入封装、等变交互块、乘积基块、读出块、原子参考能和 scale/shift。

主要覆盖：

- `LinearNodeEmbeddingBlock`
- `RadialEmbeddingBlock`
- `InteractionBlock` 及 `RealAgnostic*` 变体
- `EquivariantProductBasisBlock`
- `LinearReadoutBlock` / `NonLinearReadoutBlock`
- `AtomicEnergiesBlock`
- `ScaleShiftBlock`
- dipole readout 变体

## 输入契约

核心输入是已由 MACE datapipe 构造好的原子图张量：

- `node_attrs`: `(NumAtoms, NumElements)`，元素 one-hot
- `node_feats`: `(NumAtoms, IrrepsDim)`
- `edge_attrs`: `(NumEdges, SphericalHarmonicsDim)`
- `edge_feats`: `(NumEdges, NumRadial)`
- `edge_index`: `(2, NumEdges)`
- `batch`: `(NumAtoms,)`
- `head` / `node_heads`: 多头任务时使用

不要把普通 PyG 图字段直接当作 MACE block 输入；必须确认 irreps、元素表和近邻图已经按 MACE 约定构造。

## 输出契约

- 交互块输出：`(node_feats_next, sc_or_none)`
- product basis 输出：更新后的等变节点特征
- readout 输出：逐原子能量或 dipole 相关逐原子量
- `ScaleShiftBlock` 输出：按 head 对齐后的 scale/shift 结果

模型层会再把逐原子能量汇聚为图级能量，并由 `mace_func_utils.get_outputs` 求力、应力、virial、Hessian。

## 关键参数

- `node_attrs_irreps`
- `node_feats_irreps`
- `edge_attrs_irreps`
- `edge_feats_irreps`
- `target_irreps`
- `hidden_irreps`
- `avg_num_neighbors`
- `radial_MLP`
- `correlation`
- `use_sc`
- `heads`

OneScience demo 常见组合：

- `num_interactions=2`
- `num_channels=64/128`
- `max_L=0/2`
- `correlation=2/3`
- `radial_MLP=[64, 64, 64]`

## 典型调用位置

- `onescience.models.mace.MACE`
- `onescience.models.mace.ScaleShiftMACE`
- `AtomicDipolesMACE`
- `EnergyDipolesMACE`
- `examples/matchem/mace/train.py` 通过配置间接构建

## 常见修改点

- 改 `interaction` 类型：先确认 `INTERACTION_CLASSES` 是否已注册。
- 改 `correlation`：同步检查 `EquivariantProductBasisBlock`、checkpoint 兼容和 fine-tuning 权重迁移。
- 改 `hidden_irreps/max_L`：同步检查 readout 和 product basis 输出 irreps。
- 增加新 property：优先在模型输出和 loss 中接入，不要直接绕过 readout。
- LAMMPS/MLIAP 路径：不要破坏 ghost atoms 与 `lammps_natoms` 相关分支。

## 风险点

- `irreps` 维度不匹配会在 tensor product 或 linear wrapper 阶段报错。
- `avg_num_neighbors` 标度偏差会影响训练稳定性。
- `node_attrs` 是元素 one-hot，不是原子序数。
- `correlation=2` 与 `correlation=3` 的 contraction weights 数量不同；fine-tuning 迁移代码不能写死 weights 长度。
- `ScaleShiftMACE` 对 interaction energy 做 scale/shift，不要和普通 total energy 分解混淆。

## 下钻关系

- 径向基与 cutoff：`./mace_radial.md`
- product basis 与 contraction：`./mace_symmetric_contraction.md`
- forces/stress/virials/autograd：`./mace_func_utils.md`
- loss：`./mace_loss.md`
- fine-tuning/checkpoint：`./mace_finetuning_utils.md`
- calculator/MD/LAMMPS：`./mace_calculator.md`
- 数据协议：`../datapipes/materials_mace.md`

## 源码锚点

- `./onescience/src/onescience/modules/block/mace_block.py`
- `./onescience/src/onescience/models/mace/mace.py`
- `./onescience/src/onescience/modules/equivariant/mace_symmetric_contraction.py`
- `./onescience/src/onescience/modules/equivariant/mace_wrapper_ops.py`
