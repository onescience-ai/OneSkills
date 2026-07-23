# launch

该 datapipe 将 PDBBind/MOAD 复合物转换为 DiffDock 异构图，并在训练取样时注入扩散噪声与 score 标签。训练代码应直接用 `construct_loader`；只需要 dataset 时使用 `construct_datasets`。

```sh
python -c "from onescience.datapipes.diffdock.loader import build_noise_transform, construct_datasets, construct_loader; from onescience.datapipes.diffdock.pdbbind import PDBBind, NoiseTransform; from onescience.datapipes.diffdock.moad import MOAD; import inspect; print(inspect.signature(build_noise_transform)); print(inspect.signature(construct_datasets)); print(inspect.signature(construct_loader)); print(inspect.signature(PDBBind)); print(inspect.signature(MOAD)); print(inspect.signature(NoiseTransform))"
```

# input_schema

- `config.dataset` 支持 `pdbbind`、`moad`、`generalisation` 及受支持的 combined training。
- PDBBind 需要 `pdbbind_dir`、`split_train`、`split_val`、`cache_path`；MOAD 需要 `moad_dir`、split/cluster 元数据和 cache。
- 构图参数包括 `receptor_radius`、`c_alpha_max_neighbors`、`all_atoms`、`atom_radius`、`atom_max_neighbors`、去氢与构象匹配设置。
- 噪声参数包括 translation/rotation/torsion 的时间到 sigma 映射、`sampling_alpha/beta`、`no_torsion` 和裁剪距离。
- loader 输出 PyG `HeteroData` batch 或 data list，含 receptor/ligand 节点、边、坐标、时间特征和 translation/rotation/torsion score 标签。

# runtime_interfaces

- `construct_datasets(config, t_to_sigma, device=None)`：构造训练、验证和可选第二验证集。
- `construct_loader(config, t_to_sigma, device=None)`：构造训练/验证 loader。
- `build_noise_transform(config, t_to_sigma)`：创建 `NoiseTransform`。
- `PDBBind`、`MOAD`、`CombineDatasets`：数据集实现。
- `DataLoader` / `DataListLoader`：按设备选择 PyG batch 或 list collate。
- `NoiseTransform`：坐标加噪并生成监督 score。

# main_functions

- `construct_datasets`
- `construct_loader`
- `build_noise_transform`
- `NoiseTransform.apply_noise`
- `PDBBind.get`
- `MOAD.get`

# execution_resources

- 预处理依赖 RDKit、ProDy/PyG 等分子结构工具和可写缓存目录，主要使用 CPU。
- 大型数据集首次构图和 conformer matching 耗时较长；后续复用 pickle/cache。
- CUDA 设备默认选择 `DataListLoader`，CPU 路径选择 PyG `DataLoader`；训练器需匹配这一 batch 形式。
- 可选 ESM embedding 增加磁盘和内存需求。

# operation_limits

- 当前 loader 明确支持 PDBBind/MOAD 主路径，不支持未迁移的 pdbsidechain、triple-training 和 distillation 分支。
- 缓存键包含有限配置；更改构图参数时应使用新的 cache path，避免读取陈旧图。
- SMILES 推理构图中的 conformer 生成可能失败，此时应提供显式三维配体结构。
- 该 datapipe 只准备数据，不构造 DiffDock 模型、优化器或采样循环。
