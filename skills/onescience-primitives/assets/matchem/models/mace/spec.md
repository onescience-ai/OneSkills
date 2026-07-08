# architecture_overview
MACE 是材料原子体系的等变消息传递势函数模型，主模型以 `MACE` 和 `ScaleShiftMACE` 为核心：前者直接聚合原子参考能、短程排斥能和多层 interaction readout 的能量贡献；后者先汇总 interaction energy，再做 scale/shift 并与原子参考能相加。

模型定位：

- 输入对象：原子构型经邻居搜索后的局部图。
- 预测目标：体系总能量，以及由总能量导出的力、应力、virial、Hessian、逐原子应力等。
- 关键原理：局部邻域图 + 径向距离基 + 球谐方向基 + E(3)-等变 interaction + 高阶 product basis + 能量守恒读出。
- 辅助扩展：同文件还包含 `AtomicDipolesMACE` 与 `EnergyDipolesMACE`，用于偶极或能量-偶极联合任务，可作为 readout 设计参考。

# parameter_scale
参数规模由以下构造参数共同决定，源码中不固定给出单一参数量：

- `num_interactions`：消息传递层数，OneScience demo 常用 `2`。
- `num_channels` / `hidden_irreps`：节点等变特征通道与 irreps 规模，demo 常见 `64` 或 `128`。
- `max_ell` / `max_L`：球谐最大角动量，demo 常见 `0` 或 `2`。
- `correlation`：many-body product basis 阶数，demo 常见 `3`。
- `num_elements` 与 `atomic_numbers`：元素表大小，决定 node one-hot 与原子参考能表规模。
- `num_bessel`、`num_polynomial_cutoff`、`radial_MLP`：径向嵌入和边消息网络规模；`radial_MLP=None` 时内部使用 `[64, 64, 64]`。
- `heads`：多任务头数量；`heads=None` 时默认为 `["Default"]`。

工程判断：

- 从头训练小体系可使用较低通道数和较小角动量。
- foundation model fine-tuning 时优先继承 checkpoint 的结构参数，尤其不要随意改变 `r_max`、元素表和 hidden irreps。

# architecture_structure
主干结构按能量势函数路径组织：

输入图与物理几何
  data
    positions: (NumAtoms, 3)
    node_attrs: (NumAtoms, NumElements)
    edge_index: (2, NumEdges)
    batch: (NumAtoms,)
    cell / shifts / unit_shifts
  -> prepare_graph(...)
    vectors: (NumEdges, 3)
    lengths: (NumEdges,)
    displacement: (NumGraphs, 3, 3) 或 None
    node_heads: (NumAtoms,)

原子与边嵌入
  node_attrs
    -> LinearNodeEmbeddingBlock
    -> node_feats: scalar irreps features
  vectors
    -> spherical_harmonics(max_ell)
    -> edge_attrs: spherical harmonic irreps
  lengths + node_attrs + edge_index
    -> RadialEmbeddingBlock
    -> edge_feats: radial basis features

能量基线与可选排斥
  node_attrs
    -> AtomicEnergiesBlock
    -> node_e0 -> scatter_sum(batch) -> e0
  pair_repulsion=True
    -> ZBLBasis
    -> pair_node_energy -> scatter_sum(batch) -> pair_energy

多层等变 interaction
  repeated i in num_interactions
    node_feats, edge_attrs, edge_feats, edge_index
      -> InteractionBlock
      -> node_feats, sc
      -> EquivariantProductBasisBlock(correlation[i])
      -> node_feats
      -> LinearReadoutBlock / NonLinearReadoutBlock
      -> node_es
      -> scatter_sum(batch)
      -> energy contribution

输出聚合
  MACE
    [e0, pair_energy, interaction energies...]
      -> sum over contributions
      -> total_energy
      -> get_outputs(...)
  ScaleShiftMACE
    [pair_node_energy, readout node energies...]
      -> node_inter_es
      -> ScaleShiftBlock
      -> inter_e
      -> total_energy = e0 + inter_e
      -> get_outputs(energy=inter_e, ...)

# input_schema
`MACE.forward(data)` 和 `ScaleShiftMACE.forward(data)` 接收 PyG 风格 `dict` 或 batch，核心字段如下：

- `positions`: `(NumAtoms, 3)`，原子坐标。
- `node_attrs`: `(NumAtoms, NumElements)`，按元素表编码的 one-hot 原子类型。
- `edge_index`: `(2, NumEdges)`，有向邻接边索引。
- `batch`: `(NumAtoms,)`，每个原子所属构型编号。
- `cell`: `(NumGraphs, 3, 3)` 或单构型晶胞，周期体系和应力计算需要。
- `shifts`: `(NumEdges, 3)`，周期邻居位移。
- `unit_shifts`: `(NumEdges, 3)`，晶胞整数偏移，计算对称 displacement 时使用。
- `head`: `(NumGraphs,)` 或可广播到节点的 head id，多头任务使用。
- `ptr`: batch 指针，偶极扩展类中用于获得 `num_graphs`。
- `charges`: `(NumAtoms,)`，偶极扩展类用于固定电荷偶极基线。

构造参数默认值与关键要求：

- `pair_repulsion=False`。
- `distance_transform="None"`。
- `radial_MLP=None` 时使用 `[64, 64, 64]`。
- `radial_type="bessel"`。
- `heads=None` 时使用 `["Default"]`。
- `cueq_config=None`。
- `lammps_mliap=False`。
- `ScaleShiftMACE` 额外要求 `atomic_inter_scale` 与 `atomic_inter_shift`。

# output_schema
`MACE.forward` 返回：

- `energy`: `(NumGraphs, NumHeads)` 或可退化为 `(NumGraphs,)`，体系总能量。
- `node_energy`: `(NumAtoms,)` 或 `(NumAtoms, NumHeads)`，逐原子能量项。
- `contributions`: `(NumGraphs, NumHeads, NumContributions)` 或同义堆叠形态，能量贡献拆分。
- `forces`: `(NumAtoms, 3)`，`compute_force=True` 时由能量梯度得到。
- `edge_forces`: 边力，`compute_edge_forces=True` 或逐原子应力需要时返回。
- `virials`: `(NumGraphs, 3, 3)`，`compute_virials=True` 时返回。
- `stress`: `(NumGraphs, 3, 3)`，`compute_stress=True` 时返回。
- `atomic_virials`: 可选逐原子 virial。
- `atomic_stresses`: 可选逐原子 stress。
- `displacement`: 晶胞扰动张量，按请求返回。
- `hessian`: 可选二阶导。
- `node_feats`: 拼接后的多层节点等变特征。

`ScaleShiftMACE.forward` 额外返回：

- `interaction_energy`: scale/shift 后的相互作用能量。

偶极扩展类返回：

- `dipole`: `(NumGraphs, 3)`。
- `atomic_dipoles`: `(NumAtoms, 3)`。
- `EnergyDipolesMACE` 同时返回能量、力、应力和偶极相关字段。

# shape_transformations
数据与张量变化流程：

extxyz / xyz 构型
  train_file / valid_file / test_file
    -> Configuration
    -> AtomicData

AtomicData 图字段
  原子种类
    -> node_attrs: (NumAtoms, NumElements)
  邻居搜索
    -> edge_index: (2, NumEdges)
    -> shifts / unit_shifts: (NumEdges, 3)
  构型归属
    -> batch: (NumAtoms,)

几何预处理
  positions + edge_index + shifts
    -> vectors: (NumEdges, 3)
    -> lengths: (NumEdges,)
  compute_stress / compute_virials / compute_displacement
    -> symmetric displacement
    -> displacement: (NumGraphs, 3, 3)

特征嵌入
  node_attrs
    -> node_feats: (NumAtoms, ScalarChannels)
  lengths
    -> edge_feats: (NumEdges, RadialDim)
  vectors
    -> edge_attrs: (NumEdges, SphericalHarmonicIrreps)

等变消息传递
  node_feats + edge_attrs + edge_feats
    -> InteractionBlock
    -> EquivariantProductBasisBlock
    -> node_feats: (NumAtoms, HiddenIrreps)

能量读出
  node_feats
    -> readout
    -> node_es: (NumAtoms, NumHeads)
    -> scatter_sum(batch)
    -> graph energy: (NumGraphs, NumHeads)

物理量导出
  total_energy / interaction_energy
    -> get_outputs
    -> forces: (NumAtoms, 3)
    -> stress / virials: (NumGraphs, 3, 3)
    -> hessian / edge_forces / atomic_stresses 按开关返回

# key_dependencies
- `AtomicEnergiesBlock`：原子参考能量基线。
- `LinearNodeEmbeddingBlock`：原子 one-hot 到节点标量特征。
- `RadialEmbeddingBlock`：距离径向基与 cutoff 特征。
- `ZBLBasis`：可选短程 pair repulsion。
- `InteractionBlock`：E(3)-等变消息传递主层。
- `EquivariantProductBasisBlock`：高阶 many-body product basis。
- `LinearReadoutBlock` / `NonLinearReadoutBlock`：逐原子能量读出。
- `ScaleShiftBlock`：ScaleShiftMACE 的相互作用能量缩放和平移。
- `prepare_graph`、`get_outputs`、`get_atomic_virials_stresses`：图几何准备与物理导数输出。
- `scatter_sum`：按构型聚合逐原子贡献。

# common_modification_points
- 数据字段适配：当 extxyz 字段名不同，修改训练配置中的 `energy_key`、`forces_key`、`stress_key` 或 `virials_key`。
- 新材料体系 fine-tuning：优先设置 `foundation_model`，保留 foundation 元素表，降低学习率，并开启 EMA/SWA。
- 从头训练小体系：调整 `num_channels`、`num_interactions`、`max_L`、`correlation`、`r_max` 和 loss 权重。
- 力学/缺陷任务：提高 `forces_weight` 和必要时的 `stress_weight`，建立专门验证集检查力和应力。
- 短程排斥：对高能近邻构型或 MD 稳定性问题，可评估 `pair_repulsion=True` 的 ZBL 路线。
- 多头任务：通过 `heads` 和 `head` 字段扩展多数据源或多任务能量读出。
- LAMMPS 部署：保留 `lammps_mliap` 相关兼容分支，注意 LAMMPS 原子数切片和旧 checkpoint alias。
- 偶极任务：参考 `AtomicDipolesMACE` 或 `EnergyDipolesMACE` 替换 readout 与输出聚合路径。

# implementation_risks
- `r_max` 与 foundation checkpoint 强绑定，fine-tuning 时随意改变 cutoff 可能造成权重不匹配或性能退化。
- `E0s=average` 只是方便入口，不等价于高精度 isolated atom energies；跨 DFT 设置时需显式校准。
- `stress`、`virials` 的符号、单位和 shape 需要按数据来源单独核验。
- `energy` / `forces` 这类通用字段在 ASE 生态中可能与 calculator 字段混淆，建议数据侧使用显式参考字段。
- `node_energy` 在 `MACE.forward` 中先聚合贡献后又被重置为 `node_e0 + pair_node_energy`，使用逐原子能量解释时需核对该实现语义。
- `compute_hessian`、`compute_atomic_stresses`、`compute_edge_forces` 会显著增加自动微分开销。
- LAMMPS 分支会对节点属性和 pair energy 做原子数切片，输入 batch 与邻接边必须严格满足其接口假设。
- 偶极扩展类对 `charges`、`ptr` 和 l=1 hidden irreps 有额外要求，不能直接复用普通能量模型配置。

# code_references
- `{onescience_path}/onescience/src/onescience/models/mace/mace.py`
- `{onescience_path}/onescience/src/onescience/modules/block/mace_block.py`
- `{onescience_path}/onescience/src/onescience/modules/layer/mace_radial.py`
- `{onescience_path}/onescience/src/onescience/modules/func_utils/mace_func_utils.py`
- `{onescience_path}/onescience/src/onescience/modules/loss/mace_loss.py`
- `{onescience_path}/onescience/examples/matchem/mace/train.py`
- `{onescience_path}/onescience/examples/matchem/mace/demo/run.sh`
- `{onescience_path}/onescience/examples/matchem/mace/demo/configs/*.yaml`
- `{onescience_path}/onescience/examples/matchem/mace/scripts/eval_configs.py`
- `{onescience_path}/onescience/examples/matchem/mace/scripts/run_md.py`
