# pipeline_responsibility

targetdiff datapipe 的职责是把蛋白口袋与配体文件转换为 TargetDiff 模型使用的 `ProteinLigandData` 对象。它支持：

- `PocketLigandPairDataset`: 靶点条件小分子生成数据，通常用于 CrossDocked pocket-ligand pair。
- `PDBBindDataset`: PDBBind 亲和力/性质预测数据，带 `y` 和 `kind` 标签。
- `get_dataset`: 根据配置选择数据集并按 split 文件返回 subset。

该 datapipe 重点不是在线对接，而是构建可缓存、可批处理、带 protein/ligand 字段的图数据对象。

# pipeline_architecture

口袋-配体生成数据路径
  raw_path
    -> index.pkl
    -> pocket_fn, ligand_fn
    -> PDBProtein.to_dict_atom
    -> parse_sdf_file
    -> torchify_dict
    -> ProteinLigandData.from_protein_ligand_dicts
    -> LMDB cache
    -> transform
    -> train/test subset

PDBBind 性质数据路径
  raw_path
    -> index.pkl
    -> pocket_fn, ligand_fn, resolution, pka, kind
    -> PDBProtein.to_dict_atom
    -> parse_sdf_file_mol
    -> ProteinLigandData
    -> y / kind labels
    -> optional embedding features
    -> transform

batch 路径
  ProteinLigandData list
    -> ProteinLigandDataLoader / PyG DataLoader
    -> follow_batch fields
    -> model batch

# data_loading

- `PocketLigandPairDataset`：
  - `raw_path/index.pkl` 保存 pocket/ligand 相对路径。
  - 处理后写入同级 `{basename}_processed_{version}.lmdb`。
  - LMDB key 为样本序号字符串。
  - pocket 由 `PDBProtein(...).to_dict_atom()` 解析。
  - ligand 由 SDF 解析函数解析。
- `PDBBindDataset`：
  - `raw_path/index.pkl` 保存 pocket、ligand、resolution、pka、kind。
  - 处理后写入 `{basename}_processed.lmdb`。
  - 可选 `emb_path` 读取额外 embedding/likelihood 特征。
  - ligand 可设置 `heavy_only` 控制是否去氢。
- LMDB 读取：
  - 首次 `__len__` 或 `__getitem__` 时建立 read-only 连接。
  - 使用 cursor 收集 keys。

# sampling_strategy

- `get_dataset` 按 `config.name` 选择：
  - `pl`: `PocketLigandPairDataset`
  - `pdbbind`: `PDBBindDataset`
- 若配置包含 `split`，读取 split 文件并返回 `{split_name: Subset(dataset, indices)}`。
- 训练脚本通常取 `subsets["train"]` 和 `subsets["test"]`。
- 数据集本身按 LMDB key 顺序索引，无随机采样。
- 采样/训练时的随机性来自 DataLoader shuffle、模型采样和可选 `RandomRotation` transform。

# data_transform

- `ProteinLigandData.from_protein_ligand_dicts`：
  - protein 字段统一加 `protein_` 前缀。
  - ligand 字段统一加 `ligand_` 前缀。
  - 自动构建 `ligand_nbh_list`。
- `torchify_dict`：
  - numpy array 转 torch tensor。
- `FeaturizeProteinAtom`：
  - 元素 one-hot，支持 H/C/N/O/S/Se。
  - amino acid type one-hot。
  - backbone 标记。
  - 输出 `protein_atom_feature`。
- `FeaturizeLigandAtom`：
  - 支持 `basic`、`add_aromatic`、`full`。
  - 输出 `ligand_atom_feature_full`。
- `FeaturizeLigandBond`：
  - 将 `ligand_bond_type - 1` 转为 one-hot。
  - 输出 `ligand_bond_feature`。
- `RandomRotation`：
  - 对 ligand 和 protein 坐标施加同一个随机正交旋转。

# input_schema

- `get_dataset` 配置：
  - `name`: `pl` 或 `pdbbind`
  - `path`: 原始数据目录
  - `split`: 可选 split 文件
  - `transform.ligand_atom_mode`: `basic`、`add_aromatic`、`full`
  - `transform.random_rot`: 是否随机旋转
- `PocketLigandPairDataset` 输入目录：
  - `index.pkl`
  - pocket PDB 文件
  - ligand SDF 文件
- `PDBBindDataset` 输入目录：
  - `index.pkl`
  - pocket PDB 文件
  - ligand SDF/MOL2 文件
  - 可选 embedding 文件
- `ProteinLigandData` 基础字段：
  - protein: `element`、`pos`、`atom_to_aa_type`、`is_backbone` 等
  - ligand: `element`、`pos`、`bond_index`、`bond_type`、`center_of_mass`、`atom_feature` 等

# output_schema

- `ProteinLigandData` 字段：
  - `protein_element`
  - `protein_pos`: `(N_protein_atoms, 3)`
  - `protein_atom_to_aa_type`
  - `protein_is_backbone`
  - `ligand_element`
  - `ligand_pos`: `(N_ligand_atoms, 3)`
  - `ligand_bond_index`: `(2, N_bonds * 2)`
  - `ligand_bond_type`
  - `ligand_center_of_mass`
  - `ligand_atom_feature`
  - `ligand_nbh_list`
  - `protein_filename`
  - `ligand_filename`
  - `id`
- transform 后新增：
  - `protein_atom_feature`
  - `ligand_atom_feature_full`
  - `ligand_bond_feature`
- PDBBind 属性数据新增：
  - `y`
  - `kind`
  - 可选 `nll`、`nll_all`、`pred_ligand_v`、`final_h`、`pred_v_entropy`
- batch follow 字段：
  - `protein_element_batch`
  - `ligand_element_batch`
  - `ligand_bond_type_batch`

# constraints

- 原始目录必须包含 `index.pkl`，否则无法离线处理。
- 首次处理会创建最大约 10GB map size 的 LMDB 文件，需要可写磁盘。
- `PocketLigandPairDataset` 的 ligand 路径默认按 SDF 解析。
- `PDBBindDataset` 的 `kind` 需能映射为数值标签，`pka` 需能转 float。
- `ligand_atom_mode` 必须是 `basic`、`add_aromatic` 或 `full`。
- PyG batch 时 `ligand_nbh_list` 通常需要从 exclude keys 中排除。
- LMDB 连接对象按进程持有，多 worker 场景需注意连接生命周期。

# code_references

- `{onescience_path}/onescience/src/onescience/datapipes/targetdiff`
