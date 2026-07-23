# launch

该 datapipe 为 GenScore 构建一一配对的蛋白口袋 residue graph 与配体 atom graph。训练使用预构图的 `PDBbindDataset`，虚拟筛选/推理使用 `VSDataset` 从结构文件或 RDKit 分子实时构图。

```sh
python -c "from onescience.datapipes.genscore.data import PDBbindDataset, VSDataset; from onescience.datapipes.genscore.feats.mol2graph_rdmda_res import prot_to_graph, mol_to_graph, mol_to_graph2, load_mol; from onescience.datapipes.genscore.feats.extract_pocket_prody import extract_pocket; import inspect; print(inspect.signature(PDBbindDataset)); print(inspect.signature(VSDataset)); print(inspect.signature(prot_to_graph)); print(inspect.signature(mol_to_graph)); print(inspect.signature(mol_to_graph2)); print(inspect.signature(load_mol)); print(inspect.signature(extract_pocket))"
```

# input_schema

- `PDBbindDataset`：`ids` 为数组或 `.npy`，`ligs`/`prots` 为等长的 PyG `Data` 列表或序列化文件，`labels` 可选。
- `VSDataset`：`prot` 为口袋 PDB/RDKit Mol；`ligs` 为 SDF、MOL2、RDKit Mol 列表或 PyG 图列表。
- 从全蛋白提取口袋时设置 `gen_pocket=True`，并同时提供 `reflig` 与 `cutoff`。
- 单项输出为 `(id, protein_graph, ligand_graph, label)`；两张图至少包含 `x`、`pos`、`edge_index`、`edge_attr`。
- `train_and_test_split(valfrac=0.2, valnum=None, seed=0)` 返回训练/验证索引，而不是新 dataset。

# runtime_interfaces

- `PDBbindDataset`：读取已预处理的配体/蛋白图及标签。
- `VSDataset`：从结构输入实时构图并过滤失败配体。
- `prot_to_graph(prot, cutoff)`：构造蛋白 residue graph。
- `mol_to_graph(mol, explicit_H=False, use_chirality=True)`：构造配体 atom/bond graph。
- `mol_to_graph2(prot_path, lig_path, ...)`：同时构造一对图。
- `extract_pocket(...)`、`load_mol(...)`：口袋提取和结构读取。

# main_functions

- `PDBbindDataset.get`
- `PDBbindDataset.train_and_test_split`
- `VSDataset.get`
- `prot_to_graph`
- `mol_to_graph`
- `mol_to_graph2`
- `extract_pocket`
- `load_mol`

# execution_resources

- 构图主要使用 CPU，依赖 RDKit、MDAnalysis、ProDy、OpenBabel 与 PyTorch Geometric。
- `parallel=True` 使用 joblib 并行处理配体；大量分子时需控制内存和文件句柄。
- 口袋提取会创建并清理临时目录；输入与临时目录必须可读写。

# operation_limits

- `VSDataset` 不直接接受裸 SMILES；应先转成 RDKit Mol 或三维 SDF/MOL2。
- 参考配体坐标决定自动口袋范围，错误参考结构会产生错误蛋白图。
- 构图失败的配体会被过滤，推理器必须使用输出 `id` 映射结果，不能假设与原始顺序等长。
- 该 datapipe 不计算 GenScore 模型输出或最终亲和力分数。
