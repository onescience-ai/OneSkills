# description
DeepMD 原语用于材料/分子体系的机器学习势函数规划：当任务目标是从 AIMD/DFT 数据训练势函数，并需要能量、力、应力/维里的自动微分一致性，且下游需要与 LAMMPS/ASE/GROMACS 等经典 MD 引擎集成时，将 DeepMD 作为主模型候选。其核心规划决策包括 descriptor 类型选择（`se_e2_a` vs `DPA-3` vs `DPLR` 等）、`sel`/`rcut` 超参设定、训练数据格式与单位校验、模型冻结部署格式以及长程静电 / 自旋扩展需求。

# when_to_use
优先使用 DeepMD 的场景：
- 需要从 AIMD 数据训练经典原子间势函数，用于大规模分子动力学模拟。
- 下游部署以 LAMMPS 为目标引擎，利用 `pair_style deepmd` 原生高性能接口。
- 需要同时训练能量、力和应力，且要求通过自动微分保持物理一致性（能量守恒力）。
- 主动学习工作流（DP-GEN）中作为势函数模型，需与 labeling、训练、测试的闭环迭代集成。
- 离子/极性体系需要长程静电处理（DPLR 模型）。
- 磁性材料体系（spin 势函数）。
- 多元素复杂体系通过 DPA-3/DPA-4 预训练模型进行 fine-tuning 或 zero-shot 推理。

与 MACE 对比决策：
- 选择 DeepMD：更看重与 LAMMPS 的成熟集成、DP-GEN 生态兼容性、训练速度、无需显式图卷积和 E(3)-等变约束的简洁架构。DeepMD 通过 descriptor 的数学对称性保证不变性，训练收敛更快。
- 选择 MACE：更看重 E(3)-等变架构的表达能力、foundation model（MACE-MP/MPA/OMAT）的 zero-shot 泛化能力、或需要显式的消息传递机制。MACE 的等变 design 理论上对角度信息建模更精确，但网络更复杂、训练开销更大。

与 UMA 对比决策：
- DeepMD：LAMMPS 原生集成、成熟的 DP-GEN 主动学习生态、DPA 系列预训练模型、DPLR 长程静电支持。
- UMA：更高阶的等变消息传递架构，在某些材料体系的精度上可能优于 DeepMD 的 `se_e2_a`，但训练和推理开销通常更大，且 LAMMPS 集成不如 DeepMD 原生。

不优先使用 DeepMD：
- 任务不需要分子动力学模拟或 LAMMPS 部署，仅为学术 bench marking。
- 构型不具备局部性（如全耦合体系无法定义截断半径）。
- 数据没有可靠的能量/力标签，且无法进行 DFT 计算获取。
- 需要预测非局域电子性质（如带隙、态密度），这些超出了势函数的范畴。

# inputs
- **数据文件**：DFT 输出文件（VASP `OUTCAR`/`vasprun.xml`、CP2K、LAMMPS dump、QE、Gaussian 等）或已转换的 `dpdata` 格式数据。
- **数据字段**：坐标（`coord`）、原子类型（`type`）、能量（`energy`）、力（`force`）、可选维里（`virial`）。
- **元素信息**：`type_map`（元素名称列表）、每种原子的邻居数分布（用于确定 `sel`）。
- **物理约定**：能量单位（eV）、力单位（eV/Å）、应力单位（eV 或 bar，需转换）、晶胞格式（9 向量或 3x3 矩阵）。
- **模型配置 JSON**：
  - `model.descriptor.type`：如 `"se_e2_a"`。
  - `model.descriptor.sel`：邻居数列表。
  - `model.descriptor.rcut` 和 `rcut_smth`：截断和平滑半径。
  - `model.fitting_net.neuron`：fitting net 层结构。
  - `model.type_map`：元素列表。
- **训练配置**：初始学习率、衰减策略、`batch_size`、`numb_steps`、loss 前置因子（能量/力/应力的权重）。
- **部署目标**：LAMMPS / ASE / GROMACS / i-PI / Python API。
- **扩展需求**：是否需要 DPLR 长程静电、spin 势函数、dipole 预测、范围校正（DPRc）。
- **资源条件**：GPU/DCU 数量与显存、训练数据帧数与原子数、可接受的训练时间。

# outputs
- **选型结果**：具体 descriptor 类型（`se_e2_a`、`DPA-3` 等）、是否需要 DPLR/spin 扩展。
- **数据契约**：数据路径、格式转换脚本、元素类型映射、单位校准结果。
- **模型超参**：`rcut`、`rcut_smth`、`sel`、fitting net `neuron`、`descriptor.neuron`、`axis_neuron`。
- **训练配置 JSON**：完整输入文件，包含 model、learning_rate、training、loss 块。
- **训练与验证计划**：学习曲线（`lcurve.out`）、能量 MAE、力 MAE、应力 MAE、MD 稳定性验证、DP-GEN 迭代策略。
- **部署产物**：`frozen_model.pb`（LAMMPS/ASE 推理）、模型压缩评估结果。
- **风险清单**：`sel` 不足、`rcut` 超边界、单位错配、版本不兼容等。

# procedure
1. 确认任务是否为原子间势函数问题，明确是否需要力、应力和长程静电。
2. 使用 `dpdata` 分析训练数据：元素类型、坐标范围、晶胞尺寸、能量/力分布、邻居数分布。
3. 确定 `rcut`：推荐从 4.0-7.0 Å 中选择，确保 `rcut < 最小晶胞边长 / 2`。
4. 确定 `sel`：从邻居数分布中取 95-99 分位数的值，加上适当的余量（通常 +5~10）。
5. 选择 descriptor 类型：
   - 简单材料/液体 → `se_e2_a`。
   - 离子/极性体系 → `se_e2_a` + 评估是否需要 DPLR。
   - 磁性体系 → spin descriptor。
   - 多元素/大规模 → DPA-3/DPA-4 fine-tuning。
6. 设定 fitting net 结构：轻量级 `[120, 120, 120]`，高精度 `[240, 240, 240]`。
7. 编写训练 JSON 配置文件，设置 learning_rate、loss 权重和训练步数。
8. 运行 `dp train input.json`，监控 `lcurve.out` 学习曲线。
9. 训练收敛后，运行 `dp freeze -o frozen_model.pb` 冻结模型。
10. 测试冻结模型：`dp test -m frozen_model.pb -s test_system`，验证能量和力的误差。
11. 在 LAMMPS/ASE 中部署 frozen model，进行大规模 MD、结构弛豫或热力学计算验证。

# constraints
- **`rcut` < 最小晶胞边长 / 2**：这是硬性约束，违反将导致邻域搜索跨越多重周期边界，训练结果完全不可用。对于非正交晶胞，取三个晶胞向量的最小长度。
- **`sel` 必须大于实际邻居数**：分析训练数据中每种原子的最大邻居数，`sel` 需全覆盖；若在 DP-GEN 主动学习中数据分布变化，需重新评估 `sel`。
- **`type_map` 一致性**：训练、冻结、推理（DeepPot、LAMMPS）各阶段的 `type_map` 必须完全一致。
- **单位一致**：VASP 输出的应力单位通常是 kBar，需转换为 eV/Å³；确保数据处理链中所有能量/力/应力使用统一的单位制。
- **冻结模型版本**：`frozen_model.pb` 需与 LAMMPS 编译时使用的 DeepMD-kit 版本对应。
- **DPLR 模型的额外约束**：需要提供 Wannier center 坐标、Ewald beta 参数和 skin 参数；训练数据需包含完整的 charge 信息。
- **训练时间**：DeepMD 训练的总体时间与 `Nframes × Natoms × sel × training_steps` 成正比，大体系训练需合理估计时间成本。

# next_phase_recommendation
- 为训练数据生成一份数据卡，记录 DFT 计算参数（functional、basis set、k-points、energy cutoff）、训练/验证/测试划分比例和统计信息。
- 建立最小 benchmark：能量 MAE（meV/atom）、力 MAE（meV/Å）、应力 MAE、短 MD 能量漂移、径向分布函数（RDF）一致性。
- 对于 DP-GEN 主动学习任务，规划初始训练集大小、exploration 策略（偏差阈值）和迭代次数。
- 对于预训练模型 fine-tuning（DPA-3/DPA-4），评估预训练元素覆盖与目标体系的匹配度，规划微调数据量和学习率策略。
- 对于 LAMMPS 大规模生产运行，先做 1000 步 MD smoke test 检查能量/温度/压强的稳定性。
- 如需长程静电，先验证 DPLR 模型在短程和中程距离的能量/力精度，再扩展到全体系。

# fallback
- **`sel` 不覆盖实际邻居数**：重新分析邻居分布，更新 `sel` 后重新训练。注意 DP-GEN 主动学习迭代中新构型的邻居数可能超出初始数据统计。
- **能量/力/应力单位错配**：用 `dpdata` 检查数据的数值范围（能量应在 eV 量级，力在 eV/Å 量级），必要时通过单位因子转换或修改 DFT 输出读取参数。
- **`rcut` 超出晶胞一半**：缩小 `rcut` 或增大晶胞（超胞），这会影响物理精度和计算开销之间的平衡。对于非周期方向（slab 模型），确保真空层足够大。
- **训练不收敛（loss 震荡）**：降低学习率、增加 batch size、检查数据中是否存在异常高能构型、调整能量/力 loss 权重比例。
- **冻结模型加载失败**：检查 DeepMD-kit 版本（`dp -v`），确认 LAMMPS 编译时使用的 DeepMD 版本一致；必要时使用相同环境重新冻结。
- **力预测精度差**：增大 `forces_weight`、增加 fitting net 的 `neuron` 或层数、确保训练数据中有足够的力标签密度（每个原子都有力标签）。
- **LAMMPS MD 不稳定（温度漂移/原子飞出）**：检查训练数据是否覆盖了足够宽的构型空间（尤其是高温高压构型）、增加 `sel` 避免近邻截断、考虑添加 repulsive 修正项。
- **DPLR 结果异常**：检查 Ewald beta 参数是否适合当前体系、Wannier center 是否合理、短程部分是否在 `rcut` 范围内充分收敛。
