# launch

该 datapipe 将蛋白口袋和配体解析为 TargetDiff 所需的 `ProteinLigandData`，并用 transform 生成蛋白原子、配体原子和键特征。训练/推理代码直接调用 `get_dataset` 和 `ProteinLigandDataLoader`。

```sh
python -c "from onescience.datapipes.targetdiff import get_dataset; from onescience.datapipes.targetdiff.pl_pair_dataset import PocketLigandPairDataset; from onescience.datapipes.targetdiff.pdbbind import PDBBindDataset; from onescience.datapipes.targetdiff.pl_data import ProteinLigandData, ProteinLigandDataLoader; from onescience.utils.targetdiff.transforms import FeaturizeProteinAtom, FeaturizeLigandAtom, FeaturizeLigandBond; import inspect; print(inspect.signature(get_dataset)); print(inspect.signature(PocketLigandPairDataset)); print(inspect.signature(PDBBindDataset)); print(inspect.signature(ProteinLigandData.from_protein_ligand_dicts)); print(inspect.signature(ProteinLigandDataLoader)); print(inspect.signature(FeaturizeProteinAtom)); print(inspect.signature(FeaturizeLigandAtom)); print(inspect.signature(FeaturizeLigandBond))"
```

# input_schema

- `config.name="pl"` 使用 `PocketLigandPairDataset`，需要原始目录、`index.pkl` 及其引用的蛋白/配体文件。
- `config.name="pdbbind"` 使用 `PDBBindDataset`；可选 embedding 路径与 heavy-atom 策略由构造参数传入。
- 可选 `config.split` 指向由样本索引组成的字典；存在时 `get_dataset` 返回 `(dataset, subsets)`，否则只返回 dataset。
- `ProteinLigandData` 字段以 `protein_`/`ligand_` 前缀保存坐标、元素、原子特征、键索引/类型等。
- 默认 `follow_batch` 为 `protein_element`、`ligand_element`、`ligand_bond_type`，从而产生 TargetDiff 模型所需的 batch index。
- 默认 transform 下蛋白特征为 27 维，`add_aromatic` 配体原子类型为 13 类；改变 transform 后必须同步模型构造参数。

# runtime_interfaces

- `get_dataset(config, transform=...)`：按 `pl`/`pdbbind` 创建 dataset 和可选 subsets。
- `PocketLigandPairDataset`：LMDB 缓存的口袋—配体生成数据集。
- `PDBBindDataset`：性质/亲和力数据集。
- `ProteinLigandData.from_protein_ligand_dicts(...)`：合并两类结构字段。
- `ProteinLigandDataLoader`：带正确 `follow_batch` 的 PyG loader。
- `torchify_dict`、`get_batch_connectivity_matrix`：张量转换和按 batch 重建键矩阵。

# main_functions

- `get_dataset`
- `PocketLigandPairDataset.__getitem__`
- `PDBBindDataset.__getitem__`
- `ProteinLigandData.from_protein_ligand_dicts`
- `ProteinLigandDataLoader.__init__`
- `torchify_dict`
- `get_batch_connectivity_matrix`
- `FeaturizeProteinAtom.__call__`
- `FeaturizeLigandAtom.__call__`
- `FeaturizeLigandBond.__call__`

# execution_resources

- 首次预处理依赖蛋白/配体解析、RDKit、PyTorch Geometric 和可写 LMDB 目录，主要使用 CPU。
- 训练读取 LMDB 为只读；大型 CrossDocked 数据集需要足够磁盘和文件缓存。
- `num_workers`、batch size 和 follow-batch 张量决定主机内存；模型前向再将 batch 移到加速器。

# operation_limits

- 没有兼容 `index.pkl` 的新口袋不能直接作为 `PocketLigandPairDataset` 原始样本。
- `pl` 生成数据与 `pdbbind` 性质数据字段/标签不同，不能无条件互换。
- collate 时应排除字典字段 `ligand_nbh_list`，避免默认 PyG 拼接失败。
- LMDB 已存在时修改原始索引不会自动重建；数据版本或 transform 契约变化应使用新的缓存。
- 该 datapipe 不决定推理时每个配体的原子数，也不执行 TargetDiff 反向扩散。
