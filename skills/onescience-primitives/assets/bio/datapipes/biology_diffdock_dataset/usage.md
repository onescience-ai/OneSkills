# launch

训练脚本会通过配置构造 diffdock datapipe 和 loader：

```sh
cd "$ONESCIENCE_DIR" && python examples/biosciences/diffdock/scripts/train_diffdock.py --config examples/biosciences/diffdock/configs/training.yml
```

Python API 构造 loader 示例：

```python
from functools import partial
import torch
from onescience.datapipes.diffdock.loader import construct_loader
from onescience.utils.diffdock.diffusion_utils import t_to_sigma as t_to_sigma_compl

t_to_sigma = partial(t_to_sigma_compl, args=config)
train_loader, val_loader, val_dataset2 = construct_loader(
    config=config,
    t_to_sigma=t_to_sigma,
    device=torch.device("cuda"),
)
```

# input_schema

- 必备数据路径：
  - PDBBind: `pdbbind_dir`、`split_train`、`split_val`
  - MOAD: `moad_dir`、MOAD split pickle、cluster-to-ligand pickle
  - cache: `cache_path`
- 常用默认参数：
  - `dataset=pdbbind`
  - `batch_size=4`
  - `num_workers=1`
  - `num_dataloader_workers=0`
  - `remove_hs=true`
  - `receptor_radius=30`
  - `c_alpha_max_neighbors=10`
  - `atom_radius=5`
  - `atom_max_neighbors=8`
  - `num_conformers=1`
  - `matching_popsize=20`
  - `matching_maxiter=20`
  - `matching_tries=1`
  - `all_atoms=false`
  - `crop_beyond=20`
  - `sampling_alpha=1.0`
  - `sampling_beta=1.0`
- 推理构图输入：
  - `protein_path_list`: 蛋白 PDB 路径列表
  - `ligand_descriptions`: SMILES 或配体文件路径列表

# runtime_interfaces

- `construct_datasets`: 按配置构造 train/val 数据集。
- `construct_loader`: 构造 train/val loader，并按设备选择 batch 形式。
- `build_noise_transform`: 创建扩散噪声 transform。
- `PDBBind`: PDBBind 图数据集。
- `MOAD`: Binding MOAD 图数据集。
- `CombineDatasets`: 合并两个训练数据集。
- `DataLoader`: PyG Batch collate loader。
- `DataListLoader`: list collate loader。
- `NoiseTransform`: 训练时噪声注入和 score 标签生成。

# main_functions

- `construct_datasets`
- `construct_loader`
- `build_noise_transform`
- `get`
- `get_complex`
- `get_receptor`
- `get_ligand`
- `inference_preprocessing`
- `preprocessing`
- `apply_noise`
- `forward`

# execution_resources

- CPU 可完成预处理和缓存构建，但 RDKit/ProDy/距离矩阵计算会比较耗时。
- GPU 训练时通常使用 `DataListLoader`，CPU 或普通路径使用 PyG Batch。
- 需要可写缓存目录；首次运行会生成 pickle 缓存。
- 多进程预处理受 `num_workers` 控制，过大可能带来 RDKit/文件句柄压力。
- ESM embedding 需要额外磁盘和内存。

# operation_limits

- 不适合直接处理蛋白-蛋白、蛋白-核酸或非小分子 docking 数据。
- SMILES 推理输入依赖 RDKit conformer 生成，失败时需要换用显式 SDF/MOL2。
- MOAD 依赖固定的数据目录组织和 cluster split 文件。
- `all_atoms`、`pdbsidechain`、`distillation` 等分支在当前训练入口中不是稳定主路径。
- 若缓存已存在，参数变更不一定会覆盖旧缓存，应通过新 cache path 或清理缓存保证一致性。
