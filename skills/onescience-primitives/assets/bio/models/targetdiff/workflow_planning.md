# description

TargetDiff 的规划知识用于把“基于蛋白口袋生成候选小分子”的目标拆成口袋数据准备、扩散 checkpoint 加载、原子数策略选择、批量采样、化学重构和下游 docking/打分过滤流程。

# when_to_use

- 用户给出蛋白口袋，希望生成新的三维小分子候选。
- 任务处于药物发现 workflow 的 `target_conditioned_molecule_generation` 阶段。
- 用户需要围绕已知靶点空间探索不同原子数或多个候选分子。
- 用户需要生成后再进行 docking、GenScore 打分或 ADMET 过滤。
- 不在用户已有配体只要求对接 pose 时使用；此时应召回 DiffDock。
- 不在只要求蛋白结构生成或医学问答时使用。

# inputs

- 靶点输入：蛋白口袋结构、数据集样本 ID 或可转换为 TargetDiff 数据对象的新口袋。
- 模型输入：pretrained diffusion checkpoint、训练配置、采样配置。
- 采样输入：num samples、num steps、batch size、pos_only、center_pos_mode、sample_num_atoms。
- 资源输入：GPU、输出目录、数据集路径、图构建依赖。
- 下游需求：是否需要分子重构、有效性过滤、docking、打分或性质预测。

# outputs

- 召回决策：使用 TargetDiff 进行靶点条件分子生成。
- 执行计划：采样配置、data_id、device、batch_size、result_path。
- 结果产物：`result_{data_id}.pt`，包含生成坐标、原子类型和轨迹。
- 下游交接：将生成原子坐标/类型转为分子格式，再交给化学有效性检查、DiffDock、GenScore 或性质预测。

# procedure

1. 判断任务是否是从蛋白口袋生成新小分子，而不是对已有配体 docking。
2. 确认是否已有 TargetDiff 数据集样本；若是新口袋，先规划数据对象构建。
3. 检查 pretrained checkpoint 和训练配置中的数据路径。
4. 选择原子数策略：`prior` 用于常规生成，`ref` 用于参考配体原子数，`range` 用于扫描。
5. 设置采样数量、步数、batch size 和输出目录。
6. 运行采样并保存 `result_{data_id}.pt`。
7. 将 `pred_ligand_pos` 与 `pred_ligand_v` 转换为化学结构候选。
8. 做价态、成键、碰撞、口袋适配和重复候选过滤。
9. 对通过过滤的候选接 DiffDock/GenScore/性质预测。

# constraints

- 不能把原始坐标和原子类型直接当作可用药物分子。
- 新靶点必须经过与训练数据一致的 featurizer 和数据对象构造。
- `num_steps` 降低会加速但可能损害生成质量。
- `pos_only` 不适合完整从头分子生成。
- 下游排序必须考虑化学有效性和口袋相互作用，不能只看生成数量。

# next_phase_recommendation

- 先进行分子重构、价态修复和去重。
- 对候选做 DiffDock pose 优化或对接复核。
- 使用 GenScore 或属性预测模型进行排序。
- 对 Top-K 候选进行药化过滤、合成可行性和人工检查。

# fallback

- checkpoint 加载失败：核对路径和训练配置版本。
- data_id 无效：检查数据集 split 和样本数量。
- 显存不足：降低 `--batch_size`、`sample.num_samples` 或 `sample.num_steps`。
- 生成分子无效率高：切换 `sample_num_atoms` 策略、调整步数或加强后处理。
- 新口袋无法构图：先回退到 benchmark 数据对象，或补齐蛋白/配体 featurizer 流程。
