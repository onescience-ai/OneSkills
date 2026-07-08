# description

genscore datapipe 的规划知识用于把蛋白-配体打分任务的数据输入转换为 GenScore 所需的蛋白图、配体图、样本 ID 和标签，并根据任务是训练、虚拟筛选还是贡献分析选择预处理图路径或实时构图路径。

# when_to_use

- 训练 GenScore，需要读取预处理好的 PDBbind 图张量与标签。
- 对 SDF/MOL2 候选配体和蛋白口袋进行 GenScore 推理。
- 从全蛋白和参考配体自动生成口袋后评分。
- 需要为原子/残基贡献分析准备同一批图样本。
- 不在需要生成配体 pose 或新分子时使用。

# inputs

- 任务类型：训练、推理、贡献分析、口袋生成。
- 蛋白输入：口袋 PDB 或全蛋白 PDB。
- 配体输入：SDF/MOL2、RDKit Mol list 或预构建 PyG Data。
- 训练输入：ID 数组、ligand graph、protein graph、labels。
- 运行参数：cutoff、explicit_H、use_chirality、parallel、valnum、seed。

# outputs

- 数据决策：选择 `PDBbindDataset` 或 `VSDataset`。
- 执行计划：输入路径、口袋生成参数、图构建参数和划分策略。
- 结果产物：PyG graph dataset、训练/验证索引、推理 DataLoader 输入。
- 下游交接：将 `(id, gp, gl, label)` 交给 GenScore 模型推理或训练。

# procedure

1. 判断输入是否已预处理为 PyG 图；若是，使用 `PDBbindDataset`。
2. 若输入是结构文件，判断蛋白是否已是 pocket。
3. 若不是 pocket，要求提供参考配体和 cutoff 并调用 pocket 提取。
4. 读取 ligand 文件并按多构象切分。
5. 构建蛋白 residue graph 与配体 atom graph。
6. 过滤构图失败的 ligand，并核对 ID 数量。
7. 训练场景下用固定 seed 划分 train/val。
8. 将数据集交给 GenScore 推理或训练脚本。

# constraints

- 生成 pocket 必须有参考配体。
- 推理文件格式限制为 SDF/MOL2 或可直接传入对象。
- 训练数据必须是 PyG Data 集合。
- 图特征维度必须与 GenScore checkpoint 的 encoder 配置一致。
- 贡献分析不改变 datapipe 输出，但会增加下游评估输出。

# next_phase_recommendation

- 推理后检查 score CSV 的样本 ID 与 datapipe 输出 ID 是否一致。
- 训练前统计图数量、过滤率、label 分布和蛋白/配体节点数。
- docking 后复筛时，把上游 pose 文件名写入 ID，避免多构象混淆。
- 高分候选进入可视化、相互作用分析和物理重打分阶段。

# fallback

- pocket 生成失败：手工提供 pocket PDB。
- ligand 构图失败：转换为另一种文件格式或修复键序/坐标。
- protein graph 失败：清理 PDB、补 CA 或裁剪异常 residue。
- 图数量不匹配：输出过滤日志并重建 ID 映射。
- 特征维度不匹配：使用与 checkpoint 对应的构图参数重新预处理。
