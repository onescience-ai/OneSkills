# launch

GenScore 推理会自动调用 `VSDataset` 构建蛋白/配体图：

```sh
cd "$ONESCIENCE_DIR" && python examples/biosciences/genscore/genscore.py -p "$ONESCIENCE_DATASETS_DIR/GenScore/genscore_data/inferdata/1qkt_p_pocket_10.0.pdb" -l "$ONESCIENCE_DATASETS_DIR/GenScore/genscore_data/inferdata/1qkt_decoys.sdf" -e gatedgcn -m "$ONESCIENCE_DATASETS_DIR/GenScore/trained_models/GatedGCN_0.5_1.pth" -o examples/biosciences/genscore/out --batch_size 8 --num_workers 0
```

从全蛋白生成口袋再推理：

```sh
cd "$ONESCIENCE_DIR" && python examples/biosciences/genscore/genscore.py -p "$ONESCIENCE_DATASETS_DIR/GenScore/genscore_data/inferdata/1qkt_p.pdb" -l "$ONESCIENCE_DATASETS_DIR/GenScore/genscore_data/inferdata/1qkt_decoys.sdf" -rl "$ONESCIENCE_DATASETS_DIR/GenScore/genscore_data/inferdata/1qkt_l.sdf" -gen_pocket -c 10.0 -e gt -m "$ONESCIENCE_DATASETS_DIR/GenScore/trained_models/GT_0.0_1.pth" -o examples/biosciences/genscore/out --batch_size 8 --num_workers 0
```

Python API 构建训练数据集示例：

```python
from onescience.datapipes.genscore.data import PDBbindDataset

dataset = PDBbindDataset(
    ids="v2020_train_ids.npy",
    ligs="v2020_train_lig.pt",
    prots="v2020_train_prot.pt",
)
train_idx, val_idx = dataset.train_and_test_split(valnum=1500, seed=126)
```

# input_schema

- 训练数据准备：
  - `ids`: 一维 ID 数组，或二维数组 `[ids, labels]`
  - `ligs`: `torch_geometric.data.Data` 列表或 `.pt`
  - `prots`: `torch_geometric.data.Data` 列表或 `.pt`
  - `labels`: 可选亲和/打分标签
- 推理数据准备：
  - `prot`: pocket PDB；如果是全蛋白，则设置 `gen_pocket=true`
  - `ligs`: SDF/MOL2，多构象文件可自动切分
  - `reflig`: 生成 pocket 时必需
  - `cutoff`: 默认在示例中常用 `10.0`
  - `explicit_H=false`
  - `use_chirality=true`
  - `parallel=true`
- 训练划分默认：
  - `valfrac=0.2`
  - `seed=0`
  - `valnum=None`

# runtime_interfaces

- `PDBbindDataset`: 读取预处理训练图和标签。
- `VSDataset`: 从结构文件实时构建虚拟筛选图样本。
- `train_and_test_split`: 随机划分训练/验证索引。
- `prot_to_graph`: 蛋白 residue graph 构建。
- `mol_to_graph`: 配体 atom/bond graph 构建。
- `mol_to_graph2`: 从蛋白和配体路径同时构建两张图。
- `extract_pocket`: 从全蛋白和参考配体生成 pocket PDB。
- `load_mol`: 按文件扩展名读取分子。

# main_functions

- `get`
- `train_and_test_split`
- `prot_to_graph`
- `mol_to_graph`
- `mol_to_graph2`
- `extract_pocket`
- `load_mol`
- `_mol_to_graph`

# execution_resources

- 构图主要使用 CPU。
- 需要 RDKit、MDAnalysis、ProDy、OpenBabel 和 PyG。
- `parallel=true` 会使用 joblib 线程并行构建 ligand 图。
- 生成 pocket 会创建临时目录，完成后自动清理。
- 大量配体构图时内存占用来自 PyG Batch 和 RDKit Mol list。

# operation_limits

- 不能直接读取 SMILES；推理需要 SDF/MOL2 或 RDKit Mol。
- 口袋提取依赖 ligand 坐标和蛋白 residue 选择，参考配体不正确会导致 pocket 偏差。
- PDB 中缺 CA 时会回退 residue 原子均值，但结构质量应额外检查。
- 金属残基会归并到 `M` 类型，细粒度金属化学信息有限。
- 过滤构图失败的 ligand 后，要检查输出 ID 数量和输入构象数是否一致。
