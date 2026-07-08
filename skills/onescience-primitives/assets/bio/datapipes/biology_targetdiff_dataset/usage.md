# launch

训练扩散模型时会通过配置调用 targetdiff datapipe：

```sh
cd "$ONESCIENCE_DIR/examples/biosciences/targetdiff" && python scripts/train_diffusion.py configs/training.yml --device cuda --logdir ./logs_diffusion --tag smoke
```

采样脚本会从 checkpoint 的训练配置恢复数据集与 transform：

```sh
cd "$ONESCIENCE_DIR/examples/biosciences/targetdiff" && python scripts/sample_diffusion.py configs/sampling.yml --data_id 0 --device cuda:0 --batch_size 100 --result_path ./outputs/sample_0
```

Python API 构造数据集示例：

```python
from torch_geometric.transforms import Compose
import onescience.utils.targetdiff.transforms as trans
from onescience.datapipes.targetdiff import get_dataset

transform = Compose([
    trans.FeaturizeProteinAtom(),
    trans.FeaturizeLigandAtom("add_aromatic"),
    trans.FeaturizeLigandBond(),
])
dataset, subsets = get_dataset(config=config.data, transform=transform)
```

# input_schema

- 配置默认示例：
  - `data.name=pl`
  - `data.path=${ONESCIENCE_DATASETS_DIR}/targetdiff/data/crossdocked_v1.1_rmsd1.0_pocket10`
  - `data.split=${ONESCIENCE_DATASETS_DIR}/targetdiff/data/crossdocked_pocket10_pose_split.pt`
  - `data.transform.ligand_atom_mode=add_aromatic`
  - `data.transform.random_rot=false`
- `PocketLigandPairDataset` 参数：
  - `raw_path`
  - `transform`
  - `version=final`
- `PDBBindDataset` 参数：
  - `raw_path`
  - `transform`
  - `emb_path=None`
  - `heavy_only=false`
- DataLoader 建议：
  - `follow_batch=("protein_element", "ligand_element", "ligand_bond_type")`
  - `exclude_keys=["ligand_nbh_list"]`

# runtime_interfaces

- `get_dataset`: 根据配置创建数据集并可返回 split subsets。
- `PocketLigandPairDataset`: 口袋-配体生成数据集。
- `PDBBindDataset`: 亲和力/性质预测数据集。
- `ProteinLigandData.from_protein_ligand_dicts`: 合并 protein/ligand 字典为 PyG Data。
- `ProteinLigandDataLoader`: 默认 follow_batch 的 DataLoader。
- `torchify_dict`: numpy 到 tensor 的字段转换。
- `get_batch_connectivity_matrix`: 从 batch bond index 重建连通矩阵。
- `FeaturizeProteinAtom`: 蛋白原子特征变换。
- `FeaturizeLigandAtom`: 配体原子类型变换。
- `FeaturizeLigandBond`: 配体键特征变换。

# main_functions

- `get_dataset`
- `__getitem__`
- `get_ori_data`
- `from_protein_ligand_dicts`
- `torchify_dict`
- `get_batch_connectivity_matrix`
- `__call__`

# execution_resources

- 首次处理需要 CPU、RDKit/PDB 解析依赖和可写 LMDB 目录。
- 后续训练读取为 LMDB read-only，适合重复实验。
- 数据 transform 主要是 CPU 张量操作。
- 训练脚本使用 PyG DataLoader；batch size 由训练配置控制。
- 大型 CrossDocked 数据集会占用较多磁盘和文件缓存。

# operation_limits

- 新口袋若没有写入兼容的 `index.pkl`，不能直接走该 datapipe。
- 生成任务和性质预测任务的字段不同，不能随意互换 `pl` 与 `pdbbind` 配置。
- batch 时应排除 `ligand_nbh_list`，否则默认 collate 可能失败。
- 若 LMDB 已存在，修改原始 index 后不会自动重建，需清理旧缓存。
- 配体解析失败的样本会被跳过，训练前应统计跳过数量。
