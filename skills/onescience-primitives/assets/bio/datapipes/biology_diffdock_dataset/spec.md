# pipeline_responsibility

diffdock datapipe 的职责是为 DiffDock score/confidence 训练和采样准备蛋白-配体复合物图。它覆盖三类核心任务：

- 从 PDBBind split 文件读取复合物名称并构建训练/验证样本。
- 从 Binding MOAD cluster split 读取受体和配体，支持 cluster 采样、multiplicity 和过滤。
- 从推理输入的蛋白路径与配体描述构建临时复合物图。

输出样本是 `HeteroData`，包含 ligand、receptor、可选 atom 节点和多类边，同时训练 transform 会写入扩散时间、噪声扰动和 score 标签。

# pipeline_architecture

PDBBind 训练路径
  split_train / split_val
    -> complex names
    -> read ligand SDF/MOL2
    -> RDKit conformer and torsion matching
    -> parse receptor PDB
    -> ligand graph + receptor graph
    -> cache heterographs and rdkit ligands
    -> NoiseTransform
    -> DataLoader / DataListLoader

MOAD 训练路径
  MOAD cluster split
    -> receptor preprocessing cache
    -> ligand preprocessing cache
    -> cluster_to_ligands sampling
    -> merge receptor graph and ligand graph
    -> NoiseTransform
    -> DataLoader / DataListLoader

推理构图路径
  protein_path_list + ligand_descriptions
    -> SMILES or molecule file
    -> generate local structure if needed
    -> graph cache
    -> HeteroData

# data_loading

- PDBBind：
  - split 文件每行一个复合物名称。
  - 复合物目录内读取 `{name}_{protein_file}.pdb`。
  - 配体优先读取 `{name}_{ligand_file}.sdf`，失败后尝试 `{name}_{ligand_file}.mol2`。
  - 可选读取 ESM embedding 字典，并按 chain index 重排。
- MOAD：
  - 读取 `MOAD_generalisation_splits.pkl` 获取 split cluster。
  - 读取 `new_cluster_to_ligands.pkl` 获取 cluster 到 ligand name 的映射。
  - 受体来自 `pdb_protein/{name}_protein.pdb`。
  - 配体训练 split 来自 `pdb_superligand/{name}.pdb`，验证 split 来自 `pdb_ligand/{name}.pdb`。
- 推理：
  - 配体描述可以是 SMILES，也可以是 SDF/MOL2/PDB/PDBQT 文件。
  - SMILES 会先生成 RDKit conformer。
  - molecule 文件可选择保留本地结构或重新生成局部结构。

# sampling_strategy

- `construct_datasets` 支持 `dataset=pdbbind|moad|generalisation`，也支持 `combined_training` 合并 MOAD 与 PDBBind。
- PDBBind 按 split 文件确定 train/val 样本，`limit_complexes` 可截断样本数。
- MOAD 以 cluster 为采样单位，`get(idx)` 先定位 cluster，再从 cluster 内随机选择 ligand；`no_randomness` 时选择排序后的第一个 ligand。
- `multiplicity` 可扩大 MOAD 采样长度，`total_dataset_size` 可强制随机抽样形成固定长度数据集。
- `double_val` 可额外构造 PDBBind 验证集。
- `DataListLoader` 在 CUDA 风格加载时返回样本列表，普通 `DataLoader` 会用 PyG `Batch.from_data_list` 合并 batch。

# data_transform

- 配体处理：
  - RDKit 读取、sanitize、去氢或保留氢。
  - 原子特征包含原子序数、手性、degree、电荷、隐式价、氢数、杂化、芳香性、环信息。
  - 键边双向存储，edge_attr 为键类型 one-hot。
  - 可进行 rotatable bond matching，生成 `edge_mask` 和 `mask_rotate`。
- 受体处理：
  - ProDy 解析 PDB。
  - 以 C-alpha 坐标构建 residue graph。
  - 节点特征包含氨基酸类型和可选语言模型嵌入。
  - `side_chain_vecs` 包含 chi angle、N-CA 与 C-CA 相对向量。
  - 可选 all-atom 图和 atom-residue 边。
- 坐标处理：
  - 受体中心化，ligand 坐标同步减去 `original_center`。
  - 可按 `crop_beyond` 在噪声注入后裁剪远端受体。
- 噪声 transform：
  - 从 beta 分布采样扩散时间。
  - 计算 `tr_sigma`、`rot_sigma`、`tor_sigma`。
  - 对配体施加平移、旋转、扭转扰动。
  - 写入 `tr_score`、`rot_score`、`tor_score` 和 `tor_sigma_edge`。

# input_schema

- 配置输入：
  - `dataset`: `pdbbind`、`moad`、`generalisation`
  - `cache_path`
  - `pdbbind_dir`
  - `moad_dir`
  - `split_train`
  - `split_val`
  - `protein_file`
  - `ligand_file`
  - `batch_size`
  - `num_workers`
  - `num_dataloader_workers`
  - `remove_hs`
  - `receptor_radius`
  - `c_alpha_max_neighbors`
  - `matching_popsize`
  - `matching_maxiter`
  - `matching_tries`
  - `all_atoms`
  - `crop_beyond`
  - ESM embedding 相关路径
- 推理输入：
  - `protein_path_list`
  - `ligand_descriptions`
  - 可选 `keep_local_structures`
- diffusion transform 输入：
  - `t_to_sigma`
  - `no_torsion`
  - `sampling_alpha`
  - `sampling_beta`

# output_schema

- 单样本 `HeteroData` 字段：
  - `name`
  - `receptor_name`
  - `original_center`
  - `ligand.x`: `(N_ligand_atoms, F_ligand)`
  - `ligand.pos`: `(N_ligand_atoms, 3)` 或 conformer list
  - `ligand.edge_mask`: `(N_ligand_edges / 2,)` 风格可旋转键掩码
  - `ligand.mask_rotate`: 扭转子结构 mask
  - `ligand, lig_bond, ligand.edge_index`
  - `ligand, lig_bond, ligand.edge_attr`
  - `receptor.x`: `(N_residue, F_receptor)`
  - `receptor.pos`: `(N_residue, 3)`
  - `receptor.side_chain_vecs`: `(N_residue, feature_dim)`
  - `receptor, rec_contact, receptor.edge_index`
  - 可选 `atom.x`、`atom.pos`、atom 相关边
- 训练 transform 额外字段：
  - `complex_t`
  - `tr_score`
  - `rot_score`
  - `tor_score`
  - `tor_sigma_edge`
- loader 输出：
  - CPU/普通路径：PyG Batch
  - CUDA 风格路径：样本 list

# constraints

- 当前迁移路径明确支持 PDBBind/MOAD/generalisation；`pdbsidechain`、`distillation` 和 `triple_training` 会 fail fast。
- 训练配置中的 `all_atoms=true` 在当前示例迁移中不作为主路径。
- 受体 residue 数过大时会报错，源码中超过 3000 个 C-alpha 会拒绝处理。
- 分子文件必须可由 RDKit/ProDy 解析；配体超过 `max_lig_size` 会被过滤。
- MOAD 的 split 和 cluster pickle 路径是硬依赖。
- ESM embedding 路径存在但链顺序或序列不匹配时会影响特征拼接。
- 缓存路径由大量参数拼接，参数变化会生成新的缓存目录。

# code_references

- `{onescience_path}/onescience/src/onescience/datapipes/diffdock`
