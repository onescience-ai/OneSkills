# pipeline_responsibility

genscore datapipe 的职责是把蛋白口袋与配体构象转换为 GenScore 双图编码器可消费的 PyG 图样本。它提供两条路径：

- `PDBbindDataset`: 读取已预处理的训练/验证图张量和标签。
- `VSDataset`: 从 PDB/SDF/MOL2 或 RDKit Mol 实时构建虚拟筛选推理样本。

输出协议是 `(id, protein_graph, ligand_graph, label)`，可直接由 GenScore 推理和训练循环使用。

# pipeline_architecture

训练数据路径
  ids.npy / list
    -> pdbids
  ligand graph pt / list
    -> Batch.from_data_list
  protein graph pt / list
    -> Batch.from_data_list
  labels
    -> tensor
  PDBbindDataset.get
    -> id, gp, gl, label

推理数据路径
  protein or pocket PDB
    -> optional extract_pocket(protein, reference ligand, cutoff)
    -> load_mol
    -> prot_to_graph
  ligand SDF/MOL2
    -> split multi-ligand file
    -> RDKit Mol list
    -> mol_to_graph
  VSDataset.get
    -> id, shared protein graph, ligand graph, label

# data_loading

- 训练：
  - `ids` 可传 numpy/list，也可传 `.npy` 文件。
  - `ligs` 可传 PyG Data list，也可传 `torch.load` 得到的图列表。
  - `prots` 可传 PyG Data list，也可传 `torch.load` 得到的图列表。
  - `labels` 可显式传入；若 `ids` 文件为二维数组，第二行会作为 label。
- 推理：
  - `prot` 可为 RDKit Mol，也可为 PDB 文件路径。
  - `ligs` 支持 RDKit Mol list、PyG Data list、`.sdf` 或 `.mol2` 文件。
  - `.sdf` 按 `$$$$` 切分多构象。
  - `.mol2` 按 `@<TRIPOS>MOLECULE` 切分多分子。
  - `gen_pocket=true` 时从全蛋白与参考配体提取 pocket。

# sampling_strategy

- `PDBbindDataset.train_and_test_split` 使用随机种子从样本索引中抽取验证集。
- `valnum` 优先于 `valfrac`，默认 `valfrac=0.2`。
- `VSDataset` 没有随机采样逻辑，按输入配体块顺序生成样本。
- 推理 ID 默认来自配体 `_Name` 属性和构象序号；没有名称时使用 `lig{i}`。
- ligand 图构建可通过 joblib 并行，失败的 ligand graph 会被过滤。

# data_transform

- 蛋白/口袋图：
  - MDAnalysis 读取结构。
  - 节点为 residue。
  - residue 特征包含 32 维 residue/metal 类型、5 个内部距离特征、4 个二面角特征。
  - 以 residue 间原子最小距离小于 cutoff 建边。
  - 边特征包含序列相邻连接标记、CA 距离、质心距离、最小/最大原子距离。
  - residue 坐标按最多 24 个原子 padding，不足位置为 NaN。
- 配体图：
  - RDKit 读取 PDB/SDF/MOL2。
  - 原子特征包含元素、degree、电荷、自由基电子、杂化、芳香性、氢数和可选手性。
  - 键边双向存储，edge_attr 为键类型、共轭、环和可选立体化学。
  - 坐标来自 RDKit conformer。
- 口袋提取：
  - ligand 转 PDB 并重命名为 `LIG`。
  - 使用 ProDy 选择 ligand cutoff 范围内的蛋白残基。
  - 过滤残留 ligand 行，输出 pocket PDB。

# input_schema

- `PDBbindDataset` 输入：
  - `ids`: numpy/list 或 `.npy`
  - `ligs`: PyG Data list 或 `.pt`
  - `prots`: PyG Data list 或 `.pt`
  - `labels`: 可选
- `VSDataset` 输入：
  - `ids`: 可选
  - `ligs`: `.sdf`、`.mol2`、RDKit Mol list 或 PyG Data list
  - `prot`: PDB 路径或 RDKit Mol
  - `labels`: 可选
  - `gen_pocket`: 是否生成 pocket
  - `cutoff`: pocket 和 residue 交互截断距离
  - `reflig`: 生成 pocket 的参考配体
  - `explicit_H`: 是否保留显式氢
  - `use_chirality`: 是否使用手性特征
  - `parallel`: 是否并行构建 ligand 图

# output_schema

- `PDBbindDataset.get(idx)`：
  - `pdbid`: 样本 ID
  - `gp`: 蛋白 PyG Data
  - `gl`: 配体 PyG Data
  - `label`: 标量 tensor
- `VSDataset.get(idx)`：
  - `id`: ligand/conformer ID
  - `gp`: 共享蛋白/口袋 PyG Data
  - `gl`: 当前配体 PyG Data
  - `label`: 标量 tensor，未提供时为 0
- 蛋白图字段：
  - `x`: `(N_residue, 41)`
  - `edge_index`: `(2, N_edges)`
  - `pos`: `(N_residue, 24, 3)`
  - `edge_attr`: `(N_edges, 5)`
- 配体图字段：
  - `x`: `(N_atoms, F_atom)`
  - `edge_index`: `(2, 2 * N_bonds)`
  - `pos`: `(N_atoms, 3)`
  - `edge_attr`: `(2 * N_bonds, F_bond)`

# constraints

- 推理 ligand 文件只支持 `.sdf` 和 `.mol2`，除非直接传 RDKit Mol 或 PyG Data。
- 生成 pocket 时必须提供 `cutoff` 和 `reflig`。
- `prot_to_graph` 依赖 MDAnalysis 可正确识别 residue 和 atom 信息。
- residue padding 固定为 `RES_MAX_NATOMS=24`，异常大 residue 可能破坏 shape 假设。
- 训练图文件必须是 PyG Data 对象集合；否则会抛出类型错误。
- `_mol_to_graph` 中失败的配体会被过滤，输出数量可能少于输入构象数。

# code_references

- `{onescience_path}/onescience/src/onescience/datapipes/genscore`
