# description

DiffDock 的规划知识用于把“给定蛋白和小分子，预测/筛选结合构象”的用户目标转换为受体准备、配体准备、score 模型加载、扩散采样、confidence 重排序和结果检查的执行计划。

# when_to_use

- 用户提供蛋白 PDB 与小分子 SDF/MOL2/SMILES，希望获得对接 pose。
- 用户要对一个配体库做蛋白口袋批量 docking。
- 用户需要生成多个候选构象并按 confidence 排序。
- 当前任务处于药物发现链路的 `protein_ligand_docking` 或 `pose_generation` 阶段。
- 不在用户要求生成新分子时使用；新分子生成应考虑 TargetDiff 类模型。
- 不在用户要求医学问答、蛋白骨架生成或蛋白序列设计时使用。

# inputs

- 受体输入：PDB 路径、链 ID、是否已裁剪口袋、是否需要蛋白序列或 ESM 嵌入。
- 配体输入：SDF/MOL2/SMILES、配体名称、键序和可旋转键信息。
- 模型输入：score 模型目录、score checkpoint、可选 confidence 模型目录和 checkpoint。
- 采样输入：候选数量、扩散步数、batch size、是否启用随机初始位置、温度参数。
- 运行资源：GPU/CPU、可写输出目录、依赖是否包含几何图与分子处理库。

# outputs

- 召回决策：使用 DiffDock，以及是否启用 confidence 重排序。
- 执行计划：采样 YAML 或等价参数集合。
- 结果产物：候选配体构象、score/confidence 排序表、日志和失败诊断。
- 下游交接：将 pose 文件交给打分、MD、可视化或人工检查流程。

# procedure

1. 判断任务是否为小分子-蛋白 docking；若是蛋白设计、医学问答或分子从头生成，则改召回其它原语。
2. 召回 `biology_diffdock_dataset` datapipe，按其契约解析受体与配体并构造 DiffDock complex graph。
3. 检查受体 PDB、配体格式、键序、氢和可旋转键；必要时裁剪口袋，SMILES 输入要能生成初始构象。
4. 检查 score 模型目录中是否有 `model_parameters.yml` 和指定 checkpoint。
5. 若启用 confidence 重排序，检查 confidence 模型目录与 checkpoint 是否存在且与 score 模型类型兼容。
6. 生成采样配置：`samples_per_complex`、`batch_size`、`inference_steps`、输出目录和温度参数显式写出。
7. 运行采样脚本并观察输出 pose 数量、失败日志、显存错误和 confidence 排序。
8. 将候选 pose 交给后续重打分、构象聚类或人工可视化。

# constraints

- 不要把 DiffDock 用作亲和力回归或新分子设计模型。
- PDB 与配体文件必须能被 `biology_diffdock_dataset` 成功转成图。
- checkpoint 与模型参数必须来自同一训练配置。
- 批量模式 CSV 字段必须完整，缺字段时先补齐再执行。
- 大蛋白不应直接全量建图，优先裁剪结合口袋。

# next_phase_recommendation

- 对候选 pose 做可视化检查、RMSD/碰撞检查和基础相互作用分析。
- 需要亲和力排序时，可接 GenScore 或其它打分模型进行复筛。
- 需要进一步稳定性判断时，进入分子动力学或能量最小化流程。
- 如果输入目标来自蛋白设计链路，应记录上游蛋白结构 ID 与下游 docking 结果的映射。

# fallback

- PDB 解析失败：清理链 ID、残基编号、缺失原子和异质原子。
- 配体解析失败：转换为 SDF/MOL2，修复键序并重新生成 3D 构象。
- 模型加载失败：核对 `model_parameters.yml`、checkpoint 文件名和 old/new 模型开关。
- 显存不足：降低 `samples_per_complex`、`batch_size` 或裁剪口袋。
- confidence 模型失败：先关闭 confidence 重排序，只保留 score 模型采样结果。
