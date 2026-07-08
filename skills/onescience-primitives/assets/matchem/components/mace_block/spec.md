# component_info
`mace_block` 是 MACE 主干 block 族组件，定位为材料机器学习势函数中的等变消息传递与读出层集合。它通过直接导入方式被 `MACE`、`ScaleShiftMACE`、偶极扩展模型和训练配置间接调用，核心特征是围绕 irreps、径向边特征、元素 one-hot 与多头任务 head 组织可组合的等变网络积木。

# purpose
- 用途：构建 MACE 模型的节点嵌入、边嵌入、交互层、product basis、能量读出、偶极读出、原子参考能与 scale/shift。
- 解决问题：把局部原子图的元素、距离和方向信息转换成可聚合的逐原子能量或矢量性质。
- 适用场景：MACE/ScaleShiftMACE 训练、foundation model 微调、能量-力-应力势函数、偶极扩展、多头材料数据集任务。
- 不适用场景：裸 xyz 文本解析、近邻图构建、loss 计算、独立 CLI 推理；这些应交给 datapipe、模型层或工具层。

# input_schema
- `node_attrs`: `(NumAtoms, NumElements)`，元素 one-hot，不是原子序数。
- `node_feats`: `(NumAtoms, IrrepsDim)`，已按 `node_feats_irreps` 对齐的节点等变特征。
- `edge_attrs`: `(NumEdges, SphericalHarmonicsDim)`，球谐边属性。
- `edge_feats`: `(NumEdges, NumRadial)`，径向基或径向 MLP 特征。
- `edge_index`: `(2, NumEdges)`，有向边索引。
- `batch`: `(NumAtoms,)`，按构型聚合逐原子输出。
- `head` / `node_heads`: 多头任务 id，用于 readout、scale/shift 或 head mask。
- 约束：irreps、元素表、edge shape 和 head 数量必须与模型构造参数一致。

# output_schema
- `LinearNodeEmbeddingBlock`: 输出节点初始标量特征。
- `RadialEmbeddingBlock`: 输出经过 cutoff 的径向边特征。
- `InteractionBlock` 及 `RealAgnostic*` 变体：输出 `(node_feats_next, sc_or_none)`。
- `EquivariantProductBasisBlock`: 输出更新后的等变节点特征。
- `LinearReadoutBlock` / `NonLinearReadoutBlock`: 输出逐原子能量或多头逐原子能量。
- `LinearDipoleReadoutBlock` / `NonLinearDipoleReadoutBlock`: 输出逐原子偶极相关向量。
- `AtomicEnergiesBlock`: 输出逐原子参考能贡献。
- `ScaleShiftBlock`: 输出按 head 对齐后的 scale/shift 结果。

# parameters
- `node_attrs_irreps`: 节点属性 irreps，通常对应元素 one-hot。
- `node_feats_irreps`: 节点特征 irreps。
- `edge_attrs_irreps`: 边球谐属性 irreps。
- `edge_feats_irreps`: 径向边特征 irreps。
- `target_irreps` / `hidden_irreps`: 交互层目标与隐藏表示。
- `avg_num_neighbors`: 邻居数归一化标度。
- `radial_MLP`: 边权网络层宽，常见 `[64, 64, 64]`。
- `correlation`: product basis 相关阶数，常见 `2` 或 `3`。
- `use_sc`: 是否启用 skip connection。
- `heads`: 多头任务名称或数量。
- 常见组合：`num_interactions=2`，`num_channels=64/128`，`max_L=0/2`，`correlation=2/3`。

# key_dependencies
- `mace_radial.py`
- `mace_symmetric_contraction.py`
- `mace_wrapper_ops.py`
- `mace_irreps_tools.py`
- `mace_func_utils.py`
- `mace_loss.py`
- `mace.py`

# usage_and_risks
- 典型使用：由 `MACE` 或 `ScaleShiftMACE` 在模型初始化中组合各 block，用户通常通过训练配置间接选择 interaction 类型、correlation、hidden irreps 和 readout。
- 修改 interaction 类型时，需要确认 `INTERACTION_CLASSES` 或上层模型映射已覆盖目标类。
- 修改 `correlation` 时，需要同步检查 product basis 权重形状、checkpoint 迁移和 fine-tuning 兼容性。
- 修改 `hidden_irreps`、`max_L` 或 readout 时，需要保证所有 tensor product、linear wrapper 与输出 irreps 对齐。
- `avg_num_neighbors` 标度偏差会影响训练稳定性和能量尺度。
- `node_attrs` 元素表错位会污染原子参考能、ZBL 和 readout。
- LAMMPS/MLIAP 分支涉及 ghost atoms 与 `lammps_natoms`，不应在 block 内随意绕过。

# code_references
- `{onescience_path}/onescience/src/onescience/modules/block/mace_block.py`
- `{onescience_path}/onescience/src/onescience/models/mace/mace.py`
- `{onescience_path}/onescience/src/onescience/modules/equivariant/mace_symmetric_contraction.py`
- `{onescience_path}/onescience/src/onescience/modules/equivariant/mace_wrapper_ops.py`
