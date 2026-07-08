# architecture_overview
MatRIS 是材料领域的原子图势函数模型，全称 Material Representation Learning with Interatomic Structure。主模型为 `MatRIS`，用于从晶体或分子结构构造的 `RadiusGraph` 序列中预测能量、力、应力和磁矩。

整体设计：

- 图表示：同时维护 atom graph 和 line graph；atom graph 表示原子-邻居边，line graph 表示由两条边组成的三体角关系。
- 表征路径：原子类型、边距离、三体角度分别嵌入为 node、edge、three-body features。
- 主干更新：多层 `Interaction_Block` 交替在 line graph 与 atom graph 上做 attention 和 refinement。
- 物理读出：能量由节点特征池化得到；守恒力和应力默认来自能量对坐标与应变的自动微分；磁矩由节点特征直接读出。
- 预训练入口：`MatRIS.load` 支持加载 `matris_10m_oam` 和 `matris_10m_mp`，优先从 `ONESCIENCE_MODELS_DIR` 本地目录读取，缺失时下载到用户缓存。

# parameter_scale
源码默认配置对应一个中等规模图势函数，参数量通过 `get_params()` 动态统计。

默认构造参数：

- `num_layers=6`
- `node_feat_dim=128`
- `edge_feat_dim=128`
- `three_body_feat_dim=128`
- `mlp_hidden_dims=(128, 128)`
- `dropout=0.0`
- `use_bias=False`
- `distance_expansion="Bessel"`
- `three_body_expansion="SH"`
- `num_radial=7`
- `num_angular=7`
- `max_l=4`
- `max_n=4`
- `envelope_exponent=8`
- `graph_conv_mlp="GateMLP"`
- `activation_type="silu"`
- `norm_type="rms"`
- `pairwise_cutoff=6`
- `three_body_cutoff=4`
- `use_smoothed_for_delta_edge=False`
- `learnable_basis=True`
- `is_intensive=True`
- `is_conservation=True`
- `reference_energy=None`

预训练模型侧：

- `matris_10m_oam`：面向 OMat/OAM 路线的 10M 级预训练模型。
- `matris_10m_mp`：面向 MPTrj 路线的 10M 级预训练模型。
- 代码中保留 `matris_10m_omat`、`matris_6m_mp` 的文件名与下载占位，但当前 `load` 支持列表只接受 `matris_10m_oam` 和 `matris_10m_mp`。

# architecture_structure
主干结构按图构造、嵌入、交互、读出四段组织：

输入结构
  pymatgen.Structure / ase.Atoms
    -> GraphConverter(atom_graph_cutoff=pairwise_cutoff, line_graph_cutoff=three_body_cutoff)
    -> RadiusGraph

图批处理
  graphs: Sequence[RadiusGraph]
    -> process_graphs(graphs, compute_stress=("s" in task))
    -> batch_graph
      atomic_numbers: (TotalAtoms,)
      edge_lengths: (TotalDirectedEdges,)
      unit_edge_vectors: (TotalDirectedEdges, 3)
      atom_segment: (TotalAtoms,)
      atom_graph_dict
      line_graph_dict
      batch_cart_coords: (TotalAtoms, 3)
      batch_strains: (NumGraphs, 3, 3) 或 None

特征嵌入
  atomic_numbers - 1
    -> AtomTypeEmbedding
    -> node_feat: (TotalAtoms, node_feat_dim)

  edge_lengths + directed/undirected edge mapping
    -> EdgeBasisEmbedding(distance_expansion)
    -> edge_feat: (TotalUndirectedEdges, edge_feat_dim)
    -> smooth_weight["atom graph"]: (TotalUndirectedEdges, num_radial)
    -> smooth_weight["line graph"]: (TotalUndirectedEdges, num_radial)

  line_graph exists
    unit_edge_vectors[target_DE_index/source_DE_index]
      -> angle
      -> ThreebodyEmbedding(three_body_expansion)
      -> threebody_feat: (NumAngles, three_body_feat_dim)
  line_graph empty
      -> threebody_feat: None

多层交互
  repeated num_layers
    line graph attention/refinement
      edge_feat + threebody_feat
      -> updated edge_feat + updated threebody_feat
    atom graph attention/refinement
      node_feat + edge_feat
      -> updated node_feat + updated edge_feat

读出
  node_feat
    -> readout_norm
    -> EnergyHead
    -> total_energy: (NumGraphs,)

  task contains f/s
    -> ForceStressHead
      is_conservation=True
        total_energy -> autograd(batch_cart_coords, batch_strains)
      is_conservation=False
        edge/head direct force and equivariant stress branch
    -> f: list[(AtomsInGraph, 3)]
    -> s: list[(3, 3)]

  task contains m
    -> MagmomHead
    -> m: list[(AtomsInGraph,)]

  is_intensive=True
    total_energy / atoms_per_graph + ref_energy
    -> e: (NumGraphs,)
  is_intensive=False
    total_energy + ref_energy
    -> e: (NumGraphs,)

# input_schema
`MatRIS.forward` 输入：

- `graphs`: `Sequence[RadiusGraph]`，一个或多个结构图。
- `task`: 字符串任务标记，默认 `"ef"`；支持组合包括 `e`、`em`、`ef`、`efs`、`efsm`。
- `is_training`: 布尔值，默认 `False`；影响守恒力/应力自动微分是否保留计算图。

`RadiusGraph` 关键字段由 `GraphConverter` 生成：

- `atomic_number`: `(NumAtoms,)`，原子序数。
- `atom_frac_coord`: `(NumAtoms, 3)`，分数坐标。
- `lattice`: `(3, 3)`，晶格向量。
- `neighbor_image`: `(NumDirectedEdges, 3)` 或等价周期镜像矩阵。
- `atom_graph`: `(NumDirectedEdges, 2)`，有向原子邻接边。
- `line_graph`: `(NumAngles, 5)` 或空，三体角关系。
- `directed2undirected`: `(NumDirectedEdges,)`，有向边到无向边映射。
- `undirected2directed`: `(NumUndirectedEdges,)`，无向边到代表有向边映射。

构造参数默认值见 `parameter_scale`。关键输入约束：

- `pairwise_cutoff` 控制 atom graph 邻居范围。
- `three_body_cutoff` 控制 line graph 三体角范围。
- `reference_energy` 可选，用于加载数据集参考原子能。
- `is_intensive=True` 时输出 `e` 是每原子能量；Calculator 会按原子数换算为总能。

# output_schema
`MatRIS.forward` 返回 `dict[str, Tensor]`，字段由 `task` 和模型配置决定：

- `e`: `(NumGraphs,)`，能量；默认 `is_intensive=True` 时为每原子能量，已叠加 `ref_energy`。
- `f`: `list[Tensor]`，当 `task` 包含 `f` 时返回；每个张量形状为 `(AtomsInGraph, 3)`。
- `s`: `list[Tensor]`，当 `task` 包含 `s` 时返回；每个张量形状为 `(3, 3)`，内部以 GPa 标度生成，ASE calculator 中再转为 eV/A^3。
- `m`: `list[Tensor]`，当 `task` 包含 `m` 时返回；每个张量形状为 `(AtomsInGraph,)`。
- `atoms_per_graph`: `(NumGraphs,)`，每个图的原子数。
- `ref_energy`: `0` 或参考能张量，用于说明能量校正项。

# shape_transformations
结构到预测的张量变化：

pymatgen.Structure / ase.Atoms
  -> GraphConverter
  -> RadiusGraph
    atomic_number: (N,)
    atom_frac_coord: (N, 3)
    lattice: (3, 3)
    atom_graph: (E_directed, 2)
    line_graph: (A, 5)

多结构 batch
  graphs: List[RadiusGraph]
    -> process_graphs
    -> batch_graph
      atomic_numbers: (TotalAtoms,)
      atom_graph_dict.atom_graph: (TotalDirectedEdges, 2)
      line_graph_dict.line_graph: (TotalAngles, 3)
      edge_lengths: (TotalDirectedEdges,)
      unit_edge_vectors: (TotalDirectedEdges, 3)
      atom_segment: (TotalAtoms,)

节点嵌入
  atomic_numbers - 1
    -> embedding(max_num_elements=94)
    -> SwishLayer
    -> node_feat: (TotalAtoms, node_feat_dim)

边嵌入
  edge_lengths[undirected2directed]
    -> BesselExpansion / GaussianExpansion
    -> pairwise_rbf: (TotalUndirectedEdges, num_radial)
    -> linear + normalization + aggregate
    -> edge_feat: (TotalUndirectedEdges, edge_feat_dim)

三体嵌入
  unit_edge_vectors[target_DE_index/source_DE_index]
    -> angle
    -> FourierExpansion 或 SphericalExpansion
    -> angle_embedding
    -> threebody_feat: (TotalAngles, three_body_feat_dim)

交互层
  (node_feat, edge_feat, threebody_feat)
    -> Interaction_Block x num_layers
    -> (node_feat, edge_feat, threebody_feat)

读出与导数
  node_feat
    -> EnergyHead
    -> total_energy: (NumGraphs,)
    -> optional autograd
      force: split(TotalAtoms, 3)
      stress: list[(3, 3)]
    -> optional MagmomHead
      magmom: split(TotalAtoms,)

# key_dependencies
- `GraphConverter` / `RadiusGraph`：结构到 atom graph 与 line graph 的转换。
- `process_graphs`：多图 batch、周期边向量、应变张量与图索引组织。
- `AtomRef`：可选参考能校正。
- `AtomTypeEmbedding`：原子序数嵌入。
- `EdgeBasisEmbedding`：Bessel/Gaussian 径向边基嵌入。
- `ThreebodyEmbedding`：Fourier 或 Spherical Harmonics 三体角特征嵌入。
- `Interaction_Block`：atom graph 与 line graph 的 attention/refinement 主干。
- `EnergyHead`：节点能量读出与图级聚合。
- `ForceStressHead`：守恒或直接方式输出力和应力。
- `MagmomHead`：逐原子磁矩读出。

# common_modification_points
- 任务输出：通过 `task` 在 `e`、`f`、`s`、`m` 中选择需要的输出组合。
- 预训练权重：修改 `model_name` 为 `matris_10m_oam` 或 `matris_10m_mp`，或通过 `ONESCIENCE_MODELS_DIR/matris/` 放置本地 checkpoint。
- 图半径：调整 `pairwise_cutoff` 和 `three_body_cutoff` 控制邻居图与三体角数量。
- 模型容量：调整 `num_layers`、`node_feat_dim`、`edge_feat_dim`、`three_body_feat_dim` 与 `mlp_hidden_dims`。
- 基函数：在 `distance_expansion="Bessel"/"Gaussian"` 与 `three_body_expansion="SH"/"Fourier"` 间切换。
- 物理导数：默认 `is_conservation=True` 用能量导数得到力/应力；若需要直接力头可设为 `False` 并启用 direct branch。
- 参考能：针对不同训练集或下游能量零点，可设置 `reference_energy` 或关闭参考能校正。
- 非周期结构：ASE calculator 会扩展非周期方向 cell，裸模型调用时需自行保证结构图构造合理。

# implementation_risks
- `load` 的支持列表与 checkpoint 字典不完全一致：源码字典有 `matris_10m_omat` 和 `matris_6m_mp`，但当前 `supported_models` 只允许 `matris_10m_oam`、`matris_10m_mp`。
- 在线下载依赖外部网络；生产环境应优先设置 `ONESCIENCE_MODELS_DIR` 并放置本地 checkpoint。
- `task` 中包含 `s` 时会构造 `batch_strains` 并对能量求导，显存和时间开销高于 energy/force。
- `line_graph` 为空时三体路径跳过，模型仍能运行，但表达能力和与预训练分布的一致性可能下降。
- `AtomTypeEmbedding` 默认最大元素数为 94，超出元素表或原子序数异常会导致嵌入索引问题。
- `edge_lengths` 过小可能导致单位向量除零风险，异常重叠结构需在图构造前清洗。
- `is_intensive=True` 下输出 `e` 是每原子能量，和 calculator 中总能换算容易混淆。
- `ForceStressHead` 中 stress 标度包含 GPa 转换，跨工具比较时要确认单位。
- 大三体图超过阈值会启用 checkpoint，能省显存但增加计算时间；极大结构仍可能因 angle 数爆炸失败。

# code_references
- `{onescience_path}/onescience/src/onescience/models/matris/`
