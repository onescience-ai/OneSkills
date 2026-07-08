# description

GenScore 的规划知识用于判断何时需要对蛋白-配体候选构象进行模型打分，并把用户输入转换为口袋准备、配体读取、encoder/checkpoint 选择、score 输出和可选贡献分析的执行计划。

# when_to_use

- DiffDock 或其它 docking 流程已经产生候选 pose，需要排序或复筛。
- 用户提供蛋白口袋 PDB 和配体 SDF/MOL2，希望计算候选分数。
- 用户需要解释哪些配体原子或蛋白残基对模型分数贡献较大。
- 虚拟筛选任务需要快速批量排序候选配体。
- 不在需要生成新分子或新构象时使用；该类任务应召回 TargetDiff 或 docking 模型。

# inputs

- 蛋白输入：口袋 PDB，或全蛋白 PDB 加参考配体。
- 配体输入：SDF/MOL2，可能包含一个或多个候选构象。
- 模型输入：checkpoint 路径和 encoder 类型。
- 运行参数：batch size、num workers、cutoff、是否并行构图。
- 分析需求：常规 score、原子贡献或残基贡献。

# outputs

- 召回决策：是否使用 GenScore，以及使用 `gt` 还是 `gatedgcn` checkpoint。
- 执行计划：CLI/API 参数、输入文件、输出前缀。
- 结果产物：score CSV、原子贡献 CSV 或残基贡献 CSV。
- 下游交接：把排序后的候选交给结构检查、MD、药化过滤或报告生成。

# procedure

1. 判断任务是否为蛋白-配体打分或 docking 后排序。
2. 检查蛋白输入是否是口袋；若是全蛋白，要求提供参考配体并启用口袋生成。
3. 检查配体文件格式和构象数量。
4. 选择 encoder 和 checkpoint，确保两者匹配。
5. 判断是否需要贡献分析；若需要，选择原子或残基贡献之一。
6. 生成推理命令并显式设置 `--batch_size`、`--num_workers`、`--outprefix`。
7. 运行后检查 CSV 是否存在、score 是否可排序、样本数量是否与输入一致。
8. 将排序结果与上游 pose ID 或配体 ID 合并。

# constraints

- 原子贡献和残基贡献不能同时启用。
- 口袋生成必须提供参考配体。
- 训练和推理的特征维度必须一致。
- 不能把模型 score 直接当作实验亲和力或毒性结论。
- 输出排序应保留原始配体 ID，避免多构象混淆。

# next_phase_recommendation

- 对 Top-K 候选做可视化、碰撞检查和相互作用分析。
- 对高分候选接入更高成本的物理重打分或 MD。
- 如果来自 DiffDock，上游应保留 pose 文件路径和 confidence，便于联合排序。
- 若贡献分析显示关键残基异常，应回看口袋裁剪和输入质子化状态。

# fallback

- PDB 或配体读取失败：转换格式、清理异常原子和键序。
- 口袋生成失败：手工提供预裁剪口袋 PDB。
- checkpoint 加载失败：换用与 encoder 匹配的模型权重。
- 显存不足：降低 batch size 或切到 CPU 小批量验证。
- 分数异常集中：检查输入是否全蛋白、配体是否全部同一构象或特征预处理是否缺失。
