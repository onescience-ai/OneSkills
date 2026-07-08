# description

targetdiff datapipe 的规划知识用于把靶点条件小分子生成或蛋白-配体性质预测任务的数据准备流程拆成 index 检查、LMDB 构建、ProteinLigandData 字段验证、transform 选择、split subset 构造和 DataLoader 交接。

# when_to_use

- 训练 TargetDiff 扩散生成模型，需要 CrossDocked pocket-ligand pair 数据。
- 使用 TargetDiff 采样脚本，需要从 checkpoint 配置恢复测试集样本。
- 训练或评估 TargetDiff 属性预测网络，需要 PDBBind pocket-ligand 标签数据。
- 需要将 pocket PDB 与 ligand SDF/MOL2 组织为 protein_* / ligand_* 字段的 PyG Data。
- 不在 DiffDock pose 对接训练或 GenScore 打分图构建时使用。

# inputs

- 任务类型：分子生成、采样、性质预测。
- 数据配置：`name`、`path`、`split`、transform 设置。
- 原始文件：`index.pkl`、pocket PDB、ligand SDF/MOL2。
- 标签字段：PDBBind 的 `pka` 和 `kind`。
- 运行资源：可写 LMDB 路径、CPU、DataLoader worker、磁盘空间。

# outputs

- 数据决策：选择 `PocketLigandPairDataset` 或 `PDBBindDataset`。
- 执行计划：raw path、processed LMDB、split 文件、transform 列表。
- 结果产物：dataset、train/test subsets、ProteinLigandData batch。
- 下游交接：将 batch 交给 ScorePosNet3D 训练、采样或属性预测脚本。

# procedure

1. 判断任务是生成模型还是属性预测。
2. 根据任务设置 `config.name=pl` 或 `config.name=pdbbind`。
3. 检查 `index.pkl` 是否存在，并抽样确认 pocket/ligand 文件路径可访问。
4. 检查 processed LMDB 是否已存在；若数据或 index 变化，先规划重建。
5. 配置 transform：蛋白原子特征、配体原子模式、配体键特征和可选随机旋转。
6. 若有 split，读取 split 并确认包含 train/test 等下游脚本需要的键。
7. 构造 DataLoader，设置 follow_batch 并排除 `ligand_nbh_list`。
8. 抽样检查 batch 是否包含 protein/ligand pos、atom feature、bond feature 和 batch index。
9. 交给训练、采样或评估脚本。

# constraints

- `index.pkl` 是离线处理入口，缺失时不能自动扫描目录生成。
- LMDB 缓存不会感知原始数据更新。
- `pl` 数据通常无亲和标签，`pdbbind` 数据才有 `y/kind`。
- ligand atom mode 必须与模型 checkpoint 训练时一致。
- 新真实口袋推理需要先构造成兼容数据对象，不只是提供 PDB 文件。

# next_phase_recommendation

- 生成模型训练后，使用 sampling 配置对 test subset 做小规模采样验证。
- 属性预测训练后，按 `kind` 分组评估 Kd/Ki/IC50 等指标。
- 数据准备完成后应保存数据配置、split 和 LMDB 版本，保证采样可复现。
- 若要接 DiffDock/GenScore，下游需把 TargetDiff 输出坐标和原子类型先重构为合法分子文件。

# fallback

- index 缺失：先生成标准 index，明确 pocket/ligand 相对路径和标签列。
- LMDB 构建失败：定位具体 ligand/pocket，单独用解析函数检查。
- split 键不匹配：重写 split 文件或在脚本中改用已有键。
- batch collate 失败：排除 `ligand_nbh_list` 并确认 follow_batch 字段。
- 特征维度不匹配：核对 `ligand_atom_mode` 和 checkpoint 配置后重建数据。
