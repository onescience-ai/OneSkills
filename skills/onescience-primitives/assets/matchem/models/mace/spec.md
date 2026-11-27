# architecture_overview
MACE 是材料原子体系的等变消息传递势函数模型，主模型以 `MACE` 和 `ScaleShiftMACE` 为核心：前者直接聚合原子参考能、短程排斥能和多层 interaction readout 的能量贡献；后者先汇总 interaction energy，再做 scale/shift 并与原子参考能相加。

模型定位：

- 输入对象：原子构型经邻居搜索后的局部图。
- 预测目标：体系总能量，以及由总能量导出的力、应力、virial、Hessian、逐原子应力等。
- 关键原理：局部邻域图 + 径向距离基 + 球谐方向基 + E(3)-等变 interaction + 高阶 product basis + 能量守恒读出。
- 辅助扩展：同文件还包含 `AtomicDipolesMACE` 与 `EnergyDipolesMACE`，用于偶极或能量-偶极联合任务，可作为 readout 设计参考。

本地可复用候选 `mace-mp-0-medium-finetune-portable` 的格式为 `mace-portable-state-dict-v1`，声明类为 `onescience.models.mace.mace.ScaleShiftMACE`。它是完整 state_dict 包装及同名 companion JSON，不是可直接调用的 TorchScript 或默认 ASE 模型；文件名中的 finetune 不证明在目标界面上微调过。资源格式版本、未核实的原训练版本与本知识版本 1.0.1 分别记录。

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

该 portable companion 声明 parameter_count=4688656、state_entry_count=79；历史 CPU 反序列化检查为 79 个有限张量，浮点 dtype 为 float64。参数量来自配置声明，未通过原生构造重新计数。完整权重与 JSON 共 44225487 字节，不以文件大小代替运行主存需求。

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

所选 portable 资源必须从同身份 JSON 读取完整 `model_config`：89 元素表及其顺序、r_max=6.0 Å、num_interactions=2、max_ell=3、hidden_irreps=128x0e+128x1o、MLP_irreps=16x0e、correlation=3、radial_MLP=[64,64,64]、heads=["default"]，以及所有 atomic_energies、atomic_inter_scale/shift 和其余参数原样保留。H/C/O/K/Cu 的零基元素索引分别为 0/5/7/18/28，仅证明元素覆盖。不要手写截短的 89 项表或用默认 head 替换配置值。构图时 positions/cell 的 Å 及能量 eV、力 eV/Å 仍需核对实际训练/目标数据单位；坐标浮点计算与模型 float64 一致，索引保持整数类型。

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

原生加载软件与可选依赖边界见 [OneScience MACE 工具](../../tools/onescience-mace/usage.md)。观察到的组合为 OneScience 模块 0.3.0/发行 0.3.1、Python 3.11.15、PyTorch 2.5.1+das.opt1.dtk25042、e3nn 0.5.8、NumPy 1.26.3、ASE 3.29.0；这不是已通过的兼容推荐。JSON 的 Irreps、interaction 类和 gate 字符串须还原为原生类型，完整配置与 state_dict 同身份，不能用不同软件的默认构造参数替换。

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

原生 CPU 导入曾沿 func_utils→pangu_utils→Megatron→TransformerEngine 的可选依赖链在顶层 GPU 属性查询处报 `RuntimeError: No HIP GPUs are available`，发生在构造与 strict 加载之前。CPU 反序列化及副本重开相等只证明序列化资产，不证明原生模型兼容、目标 forward、独立精度或 MD 准入。训练血缘未提供；没有独立目标标签时科学质量仍未验证。不能以 strict=False、伪造 GPU、shadow 模块、EMT 或其他权重替代该模型验收。

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

所选资源的真实权重与完整配置入口见 [usage/launch](usage.md#launch)。已核实原生源码：
- 运行环境中 `onescience` 包中的 `models/mace/mace.py`
- 运行环境中 `onescience` 包中的 `modules/block/mace_block.py`
- [软件包入口与依赖源码](../../tools/onescience-mace/spec.md#code_references)。

# resource_acquisition

运行 MACE 前，orchestrator 必须按本契约**预检并主动获取**以下外部资源（库/权重），
不得只在文件系统里 `find` 用户产物后就停滞；任一 `on_missing: fetch` 项缺失时应先尝试获取，
获取失败再按 `degrade_to` 降级或标记 BLOCKED。所有 `sha256` 标 `待核验` 者须在首次成功下载后回填。

```yaml
resource_acquisition:
  - dep: mace-torch                       # MACE 运行库（PyPI 官方包，非同名占位包）
    kind: tool
    source:
      - {provider: pypi, id: mace-torch}
    command: |
      python3 -m pip install --upgrade pip
      python3 -m pip install mace-torch
    on_missing: fetch
    verify: "python3 -c 'import mace; print(mace.__version__)'"

  - dep: mace-mp0-universal-weights        # MACE-MP-0 通用势 foundation 权重（89 元素，微调/直接推理起点）
    kind: model_weights
    source:                                # 按优先级；沙箱无 HF 直连时用 hf-mirror 端点
      - {provider: hf-mirror,   id: cyrusyc/mace-universal, endpoint: "https://hf-mirror.com"}
      - {provider: huggingface, id: cyrusyc/mace-universal}
      - {provider: github,      id: ACEsuit/mace-foundations, note: "MACE-MP-0 / 2023-12-10-mace-128-L0_epoch-249.model 等发布权重"}
    command: |
      python3 -m pip install -U "huggingface_hub[cli]"
      export HF_ENDPOINT=https://hf-mirror.com          # 直连不可达时启用镜像
      hf download cyrusyc/mace-universal --local-dir ./mace_weights
    sha256: 待核验
    size_hint: "~数百 MB（128-L0 medium 检查点）"
    on_missing: fetch
    degrade_to: "无网络且无本地权重时，改用 ASE 内置 EMT/有效介质势做流程冒烟，并显式声明非 MACE 精度"

  - dep: lammps + mace-lammps 插件          # 仅当任务需 LAMMPS MD（如 CO2/Cu(111) 界面动力学）
    kind: tool
    source:
      - {provider: conda-forge, id: lammps}
      - {provider: github, id: ACEsuit/mace-lammps}
    command: |
      conda install -y -c conda-forge lammps            # 或按集群模块 module load lammps
      python3 -m pip install mace-lammps                # ML-IAP pair style 插件
    on_missing: fetch
    verify: "lmp -h 2>&1 | grep -i mace || python3 -c 'import mace_lammps'"
    degrade_to: "无 LAMMPS 时改用 ASE + MACECalculator 做短时 MD（ase.md），声明规模受限"
```

**获取要点（供 orchestrator 决策）**
- 微调 foundation model 时**必须继承 checkpoint 的 `r_max`、元素表、hidden irreps**（见 implementation_risks），
  下载权重后先 `MACECalculator(model_paths=...)` 做一次前向冒烟再进入训练/MD。
- 沙箱/内网环境 HuggingFace 常直连不可达：统一用 `HF_ENDPOINT=https://hf-mirror.com`；
  国内可另试 modelscope 镜像仓库。
- 若用户未提供初始结构（如 `{C12_STRUCTURE}`），本卡不负责造结构；见场景流程卡的 `input_structure` 获取/构建契约。

上述通用 foundation/ASE 路线适用于其加载器实际支持的格式。已存在的 `mace-mp-0-medium-finetune-portable` 应按 usage/launch 的完整配置与原生 strict 重构分支复用，不直接交给 `torch.jit.load` 或默认 `MACECalculator`；无须重复获取相同文件。EMT 或其他模型的流程演示不能替代该候选或本目标界面的科学验收；原生导入失败交软件工具所有者处理。

