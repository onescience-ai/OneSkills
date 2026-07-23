# architecture_overview

DiffDock 是用于蛋白-小分子对接的生成式 score 模型。它将分子对接表示为蛋白-配体复合物图上的等变扩散去噪问题，并在每个噪声时间步上预测三类 score：

- `tr`: 配体质心平移 score
- `rot`: 配体整体旋转 score
- `tor`: 配体可旋转键扭转 score

主模型以 `CGModel` 为默认采样路径，`AAModel` 提供更细粒度的受体原子交互建模。两者都围绕配体图、受体图和蛋白-配体交叉图组织消息传递，并用球谐特征与张量积卷积保持几何等变性。

# parameter_scale

- 默认标量通道 `ns=16`
- 默认向量通道 `nv=4`
- 默认张量球谐阶数 `sh_lmax=2`
- 默认卷积层数 `num_conv_layers=2`
- 默认配体局部半径 `lig_max_radius=5`
- 默认受体局部半径 `rec_max_radius=30`
- 默认蛋白-配体交叉距离 `cross_max_distance=250`
- 默认中心卷积距离 `center_max_distance=30`
- 默认距离展开维度 `distance_embed_dim=32`
- 默认交叉距离展开维度 `cross_distance_embed_dim=32`
- 默认 sigma 嵌入维度 `sigma_embed_dim=32`
- confidence 模式可输出复合物级置信度与可选原子级置信度

# architecture_structure

输入分支组织
  ligand graph
    -> AtomEncoder(lig_feature_dims)
    -> ligand edge GaussianSmearing
    -> ligand TensorProductConvLayer
  receptor residue graph
    -> AtomEncoder(rec_residue_feature_dims)
    -> receptor edge GaussianSmearing
    -> receptor TensorProductConvLayer
  receptor atom graph
    -> AtomEncoder(rec_atom_feature_dims)
    -> atom edge GaussianSmearing
    -> all-atom interaction branch
  ligand-receptor cross graph
    -> cross distance expansion
    -> ligand-to-receptor / receptor-to-ligand message passing

Score 输出头
  ligand node features
    -> center graph convolution
    -> translation vector score
    -> rotation vector score
    -> torsion bond graph convolution
    -> torsion angle score

Confidence 输出头
  ligand node features
    -> graph-level scatter_mean
    -> confidence predictor
    -> optional atom confidence predictor

# input_schema

- `model_dir`: 必须包含 `model_parameters.yml` 与 score checkpoint。
- `ckpt`: score 模型权重文件名，常见值为 `best_ema_inference_epoch_model.pt`。
- `data`: 采样时传入的蛋白-配体异构图，至少包含：
  - `ligand.x`: 配体原子离散/连续特征
  - `ligand.pos`: 配体原子坐标
  - `ligand.edge_index`: 配体键图
  - `ligand.edge_mask`: 可旋转键掩码
  - `ligand.batch`: batch 索引
  - `receptor.x`: 受体残基特征
  - `receptor.pos`: 受体残基坐标
  - `complex_t.tr`, `complex_t.rot`, `complex_t.tor`: 扩散时间或噪声水平
- 可选输入：
  - ESM/语言模型嵌入
  - 受体原子级特征
  - confidence 模型目录与 checkpoint
  - CSV 批量输入，字段包含 `complex_name`、`protein_path`、`ligand_description`、`protein_sequence`

# output_schema

- score 模式：
  - `tr_pred`: `(num_graphs, 3)`，配体平移 score
  - `rot_pred`: `(num_graphs, 3)`，配体旋转 score
  - `tor_pred`: `(num_rotatable_bonds,)`，扭转 score；无可旋转键时为空张量
  - `sidechain_pred`: 可选侧链预测结果，默认通常为 `None`
- confidence 模式：
  - `confidence`: 复合物级置信度或置信度/亲和力聚合输出
  - `atom_confidence`: 原子级置信度，未启用时为零张量
- 上层采样输出：
  - 候选配体构象文件
  - 采样日志
  - confidence 重排序结果

# shape_transformations

复合物图构建
  ligand nodes: (N_lig, F_lig)
    -> ligand node attr: (N_lig, hidden irreps)
  receptor residue nodes: (N_rec, F_rec)
    -> receptor node attr: (N_rec, hidden irreps)
  receptor atom nodes: (N_atom, F_atom)
    -> atom node attr: (N_atom, hidden irreps)

边与几何特征
  pairwise distances
    -> GaussianSmearing: (N_edges, distance_embed_dim)
    -> spherical harmonics: (N_edges, sh_irreps)
    -> TensorProductConvLayer

去噪输出
  ligand node attr
    -> center graph: (N_lig -> num_graphs)
    -> global_pred
    -> tr_pred / rot_pred
  rotatable bond graph
    -> tor_bond_conv
    -> tor_pred: (N_rotatable_bonds,)

# key_dependencies

当前没有与 DiffDock 模型内部层一一对应的 bio component primitive。训练和推理的数据构图应另外召回 `biology_diffdock_dataset` datapipe；模型结构与加载接口直接使用本模型资源。

# common_modification_points

- 在轻量采样场景优先使用 `CGModel`；需要更细受体原子交互时再考虑 `AAModel`。
- 调整采样质量与速度时优先改 `sampling.inference_steps`、`samples_per_complex`、`batch_size` 和 temperature 系列参数。
- 需要增强蛋白语义特征时启用或预计算 ESM embedding，并保证 `model_parameters.yml` 中相关路径可用。
- 需要 confidence 重排序时提供 confidence 模型目录；若只做快速 pose 生成，可先关闭重排序。
- 想改交互范围时优先调整 `lig_max_radius`、`rec_max_radius`、`cross_max_distance`，避免直接改等变卷积内部结构。
- 想做无扭转或刚性配体采样时检查 `no_torsion` 与 `ligand.edge_mask`。

# implementation_risks

- 输入 PDB、SDF/MOL2 或 SMILES 解析失败会阻断图构建，通常需要先清理氢、键序、链 ID 和口袋区域。
- `model_parameters.yml` 与 checkpoint 必须匹配，结构参数不一致会导致权重加载失败。
- 启用语言模型嵌入时需要 ESM 依赖或预计算嵌入路径，否则会在模型初始化阶段失败。
- `AAModel` 中部分功能仍有未实现分支，例如 sidechain prediction、depthwise convolution、crop beyond 的原子过滤。
- 扭转 score 依赖配体可旋转键掩码；无可旋转键时 `tor_pred` 为空，不应被下游当作失败。
- 蛋白-配体交叉边过多会显著增加显存与耗时，长蛋白或大 batch 应先裁剪口袋。

# code_references

- `{onescience_path}/onescience/src/onescience/models/diffdock`
