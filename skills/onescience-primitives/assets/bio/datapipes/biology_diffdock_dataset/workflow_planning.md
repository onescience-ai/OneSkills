# description

diffdock datapipe 的规划知识用于判断何时需要把蛋白-小分子复合物数据转换为 DiffDock 可训练/可采样的异构图，并把数据准备拆成 split 检查、分子解析、受体构图、缓存生成、噪声 transform 和 loader 构造。

# when_to_use

- 训练 DiffDock score 模型或 confidence 模型，需要 PDBBind/MOAD 复合物图。
- 对蛋白 PDB 和配体 SMILES/SDF/MOL2 做 DiffDock 推理前构图。
- 需要把 docking 数据转换为含平移/旋转/扭转 score 标签的训练 batch。
- 需要合并 PDBBind 与 MOAD 训练数据。
- 不在纯蛋白结构预测、医学文本问答或靶点条件新分子生成任务中使用。

# inputs

- 数据模式：PDBBind、MOAD、generalisation、combined training。
- 原始数据路径：复合物目录、split 文件、MOAD cluster 文件、cache 目录。
- 分子/蛋白处理参数：去氢、最大配体大小、受体半径、最大邻居数、扭转匹配参数。
- 扩散参数：`t_to_sigma`、是否禁用 torsion、采样 beta 分布参数、crop 距离。
- 运行资源：CPU worker、GPU/CPU loader 策略、缓存磁盘空间。

# outputs

- 数据决策：使用 PDBBind、MOAD 或组合数据集。
- 执行计划：数据目录、split、缓存路径和 loader 构造参数。
- 结果产物：train loader、val loader、可选第二验证集、缓存 pickle。
- 下游交接：将 batch 交给 DiffDock score/confidence 训练或采样流程。

# procedure

1. 判断任务是否需要 DiffDock 复合物图。
2. 选择数据模式：PDBBind、MOAD、generalisation 或 combined training。
3. 检查 split 文件、复合物目录、MOAD cluster pickle 和缓存目录。
4. 确认配体格式和受体 PDB 命名约定。
5. 设置构图半径、邻居数、去氢、扭转匹配和最大配体大小。
6. 构造 `NoiseTransform`，确认 `t_to_sigma` 与模型训练参数一致。
7. 调用 dataset/loader 构造并观察缓存生成日志。
8. 抽样检查 batch 字段：ligand/receptor 坐标、edge_index、edge_mask、score 标签。
9. 将 loader 交给训练脚本。

# constraints

- split 中的复合物名称必须与数据目录一致。
- 受体过大、配体过大、RDKit sanitize 失败都会导致样本跳过。
- 训练入口不应启用尚未迁移的分支。
- 缓存与参数强绑定，复用缓存前必须确认参数一致。
- 扭转训练依赖 `edge_mask` 和 `mask_rotate`，无可旋转键时要允许 `tor_score` 为空。

# next_phase_recommendation

- loader 构造成功后，先运行小步 smoke training 验证 loss 和 batch 字段。
- 若要训练 confidence 模型，先保存 score 模型输出目录并复用同源数据划分。
- 推理场景下，将构图结果交给 DiffDock sampling，并保留 `original_center` 用于坐标还原。
- 数据质量审计应统计样本跳过率、配体大小、受体大小和 matching RMSD。

# fallback

- split 或目录不匹配：先生成样本名清单并核对文件命名。
- RDKit 读取失败：改用另一种配体格式或预先 sanitize。
- 受体解析失败：清理 PDB、去除异常链或裁剪口袋。
- 缓存污染：换新 cache path 或删除旧缓存后重建。
- 显存不足：降低 batch size、关闭 all-atom、减小受体半径或使用 CPU collate。
