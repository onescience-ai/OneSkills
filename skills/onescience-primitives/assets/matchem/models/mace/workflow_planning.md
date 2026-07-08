# description
MACE 原语用于材料原子体系的机器学习势函数规划：当任务目标是从原子构型学习能量面，并需要能量守恒的力、应力、virial 或下游 MD/结构弛豫能力时，优先把 MACE 作为主模型候选。规划重点不是只选择网络层数，而是同时约束数据字段、元素表、cutoff、原子参考能、loss 权重、foundation checkpoint 和部署路径。

# when_to_use
- 需要训练或微调材料体系 MLIP。
- 需要预测总能量，并通过自动微分获得力、应力、virial 或 Hessian。
- 目标数据是晶体、缺陷、表面、吸附、液体、界面、固态电解质或分子材料构型。
- 需要把模型接入 ASE、LAMMPS、MD 或结构弛豫流程。
- 小数据材料任务可使用 MACE-MP、MACE-MPA、MACE-OMAT 或本地 `.model` 做 fine-tuning。

不优先使用：

- 输入不是原子构型或无法形成局部邻域图。
- 任务只需要全局标量回归且不需要物理梯度一致性。
- 数据没有可靠的能量/力标签，且无法校准单位和参考能。

# inputs
- 数据文件：`train_file`、`valid_file` 或 `valid_fraction`、`test_file`。
- 字段映射：`energy_key`、`forces_key`、可选 `stress_key` / `virials_key`。
- 元素信息：元素种类、`AtomicNumberTable`、是否保留 foundation model 全元素表。
- 物理约定：能量单位、力单位、stress/virial 符号与 shape。
- 模型配置：`r_max`、`num_interactions`、`num_channels`、`max_L`、`correlation`、`E0s`。
- 训练目标：能量精度、力精度、应力精度、MD 稳定性或部署格式。
- 资源条件：单卡/多卡、CPU 核数、最大构型规模、训练时限。
- 是否微调：`foundation_model`、checkpoint 来源、预训练模型元素表与 cutoff。

# outputs
- 选型结果：`MACE`、`ScaleShiftMACE` 或偶极扩展类。
- 数据契约：输入文件格式、字段名、单位、元素表和划分策略。
- 模型超参：cutoff、层数、通道数、角动量、相关阶数、径向基设置。
- 训练配置：loss 权重、batch size、学习率、EMA/SWA、早停和评估间隔。
- 运行方式：demo YAML、直接训练命令、dry-run 检查结果和输出目录策略。
- 验证计划：能量 MAE、力 MAE、stress/virial 检查、MD 稳定性和部署 smoke test。
- 风险清单：字段不匹配、单位错配、cutoff 不兼容、元素缺失、内存不足和下游不稳定。

# procedure
1. 确认任务是否是原子尺度势函数问题，并判断需要 energy-only、energy-force、energy-force-stress 还是偶极扩展。
2. 检查 extxyz/xyz 数据字段，明确 `energy_key`、`forces_key`、`stress_key` 或 `virials_key`，抽样核对单位和 shape。
3. 建立元素表和原子参考能策略：小规模可从 `isolated` 或显式 E0s 开始，跨 DFT 设置时避免盲用 `average`。
4. 选择训练路线：
   - 数据少或体系接近预训练覆盖范围：使用 `foundation_model` 微调。
   - 数据量充足或体系差异大：从头训练并显式搜索 `r_max`、`num_channels`、`max_L`。
5. 设定模型结构：先用 demo 稳定配置作为 baseline，再按精度和显存调整通道数、角动量和 interaction 层数。
6. 设定 loss 权重：力主导任务提高 `forces_weight`，含晶胞力学任务加入并核验 `stress_weight`。
7. 运行 `run.sh --dry-run`，检查数据文件、环境变量、launcher、输出目录和最终训练命令。
8. 执行短训练 smoke test，确认 forward、loss、checkpoint 和评估表正常。
9. 完整训练后用测试集、异常构型和下游 MD/relaxation 评估模型。
10. 若要部署到 LAMMPS 或 ASE，单独验证导出模型与原训练模型在同一 batch 上输出一致。

# constraints
- 不改变 foundation checkpoint 的关键结构约束，尤其是 `r_max`、元素表和 hidden irreps，除非明确重新初始化相关权重。
- 数据字段和单位必须在训练、验证、评估、部署中保持一致。
- 含应力训练时必须明确 stress 与 virial 的转换关系、符号和体积归一化。
- 大体系训练受边数主导，不能只按原子数估算显存。
- 多卡训练应通过项目 demo 入口生成命令，先 dry-run 再提交。
- `compute_hessian` 和逐原子 stress 只在必要时开启。

# next_phase_recommendation
- 为目标材料体系补充一份数据卡，记录字段名、单位、元素表、DFT 设置和 train/valid/test 划分。
- 建立最小 benchmark：能量 MAE、力 MAE、stress MAE、短 MD 稳定性、结构弛豫收敛性。
- 对 foundation fine-tuning 任务，优先比较 `medium`、`medium-mpa-0`、`medium-omat-0` 与本地 checkpoint。
- 对部署任务，增加 ASE 与 LAMMPS 一致性测试，并固定导出脚本和环境版本。
- 若任务涉及偶极或电荷相关性质，再规划 `AtomicDipolesMACE` 或 `EnergyDipolesMACE` 分支。

# fallback
- 字段名不匹配：先统一 extxyz 字段或修改 `energy_key`、`forces_key`、`stress_key`，不要在模型层临时修补。
- 单位或 stress/virial 约定不明：暂停训练，抽样回查数据生成流程并做小批量数值验证。
- foundation model 加载失败：检查元素表、cutoff、head、checkpoint alias 和本地缓存；必要时改为从头训练 baseline。
- 显存不足：降低 `batch_size`、`num_channels`、`max_L` 或邻域 cutoff，先保持物理字段正确。
- MD 不稳定：增加异常近邻构型、检查短程排斥、重新权衡力和应力损失，并用更严格验证集筛选 checkpoint。
- LAMMPS/ASE 输出不一致：固定同一构型做逐项对比，优先检查元素顺序、单位、cell、periodic shifts 和导出路径。
