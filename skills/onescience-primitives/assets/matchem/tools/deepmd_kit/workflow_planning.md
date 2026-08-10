# description
DeepMD-kit 原语用于从第一性原理数据训练原子间机器学习势函数（MLIP）并部署到 MD 引擎的工作流规划。当任务目标是从 DFT 计算数据学习势能面，并将高精度量子力学模型转化为可用于大规模经典 MD 模拟的力场时，DeePMD-kit 是核心工具。规划重点不仅是模型结构选择（descriptor 类型），还需同时约束数据质量、训练策略、模型操作和部署路径。

# when_to_use
优先使用 DeepMD-kit 的场景：

- 需要从 VASP/CP2K/LAMMPS/QCHEM 等 DFT 计算结果中训练原子间势函数（MLIP）。
- 目标体系是周期性晶体、表面、界面、缺陷、液体、电解质、二维材料或分子体系。
- 训练数据包含能量、力和（可选的）应力/virial 标签。
- 训练完成后需要将模型部署到 LAMMPS（pair_style deepmd）、ASE、GROMACS 或 i-PI 进行大规模 MD 模拟。
- 需要通过 Model Deviation 评估模型不确定性，并计划接入 DP-GEN 主动学习流程。
- 在使用 DPA-3 等预训练模型进行 fine-tuning，以降低数据需求。
- 需要处理长程静电（DPLR）或磁性体系（spin DP）。
- 需要多任务训练（同时拟合不同 DFT 设置或多种物理量数据）。

不优先使用 DeepMD-kit：

- 任务直接进行第一性原理计算（应使用 VASP/CP2K/QE 等）。
- 只需要经典力场 MD 模拟，不涉及第一性原理训练数据（直接用 LAMMPS 内置势函数即可）。
- 数据量极小（< 100 个构型），且无合适的预训练模型可用。
- 非原子尺度任务（如粗粒化模拟、介观模拟、有限元分析）。
- 对推理延迟要求极高但可以接受经典力场精度的场景。

# inputs
规划 DeePMD-kit 工作流需要明确以下输入：

- **数据来源**：DFT 计算软件（VASP/CP2K 等）和输出格式，数据量大小（构型数、原子数范围）。
- **数据质量**：能量/力/应力标签的单位、符号约定，构型覆盖的温度/压力/化学空间范围。
- **元素信息**：元素种类和数量，每种元素的原子参考能（atom_ener）。
- **物理需求**：仅训练能量还是同时训练力/应力，是否需要偶极/极化率/DOS。
- **模型策略**：从头训练还是 fine-tuning 预训练模型（DPA-3 等）。
- **精度目标**：能量 RMSE（meV/atom 级别）、力 RMSE（meV/Å 级别）。
- **性能需求**：部署场景（LAMMPS/ASE），推理速度要求（是否需压缩），体系规模。
- **资源条件**：GPU 数量、单卡显存、CPU 核数、DFT 计算资源预算。
- **是否需要主动学习**：是否接入 DP-GEN 流程。

# outputs
- 模型选型：descriptor 类型（se_e2_a / se_e2_r / se_e3 / se_atten / DPA-3 / hybrid）。
- 数据契约：训练数据需转换为 DeePMD-kit native system 格式，明确 train/valid/test 划分策略。
- input.json 配置：完整的 descriptor + fitting_net + learning_rate + loss + training 参数。
- 训练方案：训练步数、batch_size、学习率调度、多 GPU 策略。
- 模型产出：冻结模型文件（.pb/.pth），可选压缩模型。
- 精度报告：dp test 输出（能量/力/virial RMSE），model deviation 分析结果。
- 部署方案：LAMMPS/ASE 接口配置，type_map 映射。
- 风险清单：sel 不足、rcut 不匹配、单位不一致、原子参考能错误、type_map 错配。

# procedure
1. **数据收集与评估**：从 DFT 计算结果中收集原子构型+能量+力+应力数据。检查数据质量：
   - 统一单位（推荐 eV/Å）。
   - 检查能量范围、力分布、原子距离是否有异常。
   - 评估构型覆盖的相空间是否足够（温度、压强、化学组成）。
2. **数据预处理（dpdata）**：将原始数据转换为 DeePMD-kit native system 格式。
   - 通过 `dpdata.LabeledSystem` 读取原始数据。
   - 使用 `sub_system()` 按条件筛选构型。
   - 随机划分 train/valid/test，建议 8:1:1 或 9:1。
   - 输出 `set.*/` 格式的二进制数据。
3. **选择训练路线**：
   - 数据量充足（> 10^3 构型）：从头训练，从 se_e2_a 开始。
   - 数据量少（< 10^3 构型）或体系接近预训练覆盖范围：使用 DPA-3 fine-tuning。
   - 多元素/强方向性体系：se_e2_a 或 se_atten。
   - 仅径向相互作用：se_e2_r。
4. **设定模型超参数**：
   - `rcut`：根据体系中化学键和分子间相互作用的典型距离确定（4-7 Å）。
   - `sel`：根据最大配位数设定，预留 20-50% 余量。
   - descriptor `neuron`：经典配置 [25, 50, 100]。
   - fitting_net `neuron`：经典配置 [240, 240, 240]。
   - fine-tuning 时继承预训练模型的 rcut 和 sel，不可随意更改。
5. **设定 loss 权重**：
   - 力导向任务：`start_pref_f` = 1000。
   - 含应力训练：`start_pref_v` > 0（如 0.02）。
6. **编写 input.json**：确保所有路径正确，参数无拼写错误。
7. **执行训练**：
   - 小数据 walk test：用少步数快速验证（`numb_steps: 1000`），确认 loss 下降。
   - 正式训练：设置充足步数（10^5-10^6），监控 `lcurve.out`。
8. **验证模型**：
   - `dp test` 在独立测试集上评估精度。
   - 使用 model deviation 检查模型置信度。
   - 如有问题，调整 descriptor/fitting_net 参数或增加训练数据后重新训练。
9. **冻结与压缩**：
   - `dp freeze`：将最佳 checkpoint 冻结为 .pb 文件。
   - `dp compress`：压缩模型，再用 `dp test` 验证压缩后精度无明显退化。
10. **部署与验收**：
    - LAMMPS：用压缩模型在 LAMMPS 中运行短 MD 验证能量守恒、力精度。
    - ASE：运行结构弛豫测试（BFGS/FIRE）。
    - 对比 DeePMD-kit 原生推理与 LAMMPS/ASE 输出一致性。

# constraints
- 不同 descriptor 与 fitting_net 类型之间有兼容性约束（如 "se_e2_a" descriptor 必须配 "ener" fitting_net 用于能量训练）。
- `rcut` 和 `sel` 在 fine-tuning 时必须匹配预训练模型，否则无法加载 checkpoint。
- 能量/力/应力标签必须在整个流程中保持单位一致。
- 训练数据的元素类型编号（type.raw）必须与模型的 type_map 严格对应。
- LAMMPS 中原子类型 ID 与 DP 模型 type_map 的映射需要额外小心，顺序错位会导致静默计算错误。
- 对于多 GPU 训练，Horovod 环境需要正确配置（NCCL/MPI）。
- TensorFlow 模型无法直接在 PyTorch 加载，反之亦然。

# next_phase_recommendation
- 补充目标体系的数据卡：记录 DFT 设置（functional、basis、k-points、ENCUT）、数据量、元素表、温度/压力范围。
- 建立 benchmark 基线：能量 MAE/力 MAE 最小值目标值、MD 稳定性标准（NVE 能量漂移 < 1e-4 eV/atom/ps）。
- 对比不同 descriptor 组合：se_e2_a vs se_e3 vs se_atten 在同数据集上的表现。
- 对 fine-tuning 任务：对比 DPA-3 fine-tune 与从头训练在目标体系上的精度差距。
- 规划 model deviation 阈值：根据体系化学键强度确定 σ_low 和 σ_high 阈值（能量/力）。
- 对部署任务：建立 LAMMPS 一致性和稳定性验收标准。

# fallback
- **训练不收敛**：检查数据质量（单位、异常值、构型覆盖），降低学习率，调整 loss 权重（增大 forces_weight）。
- **模型精度不足**：增大 rcut 使其覆盖更长程相互作用，增加 sel 避免邻居丢失，尝试 se_atten 或 se_e3。
- **显存不足**：降低 batch_size，减小 sel，减小 rcut，降低 descriptor/fitting_net neuron 数。
- **MD 模拟崩溃**：检查是否有近邻原子距离过小（检查 `min_nbor_dist` 在压缩配置中的设置），提高配位数设置（sel），加入短程排斥模型（通过数据覆盖近邻构型）。
- **model deviation 分布偏斜**：调整 ensemble 模型训练策略（不同初始化种子、不同数据子集），调整 σ_low/σ_high 阈值。
- **LAMMPS 与 dp test 结果不一致**：逐一检查：type_map 映射、units 设置、periodic boundary 条件、cell 参数、原子排序。
- **压缩后精度严重退化**：减小 `table_config` stride（如 0.01→0.005），增加插值表范围，增大 `min_nbor_dist`。

# teaming_with_dpgen
DeepMD-kit 与 DP-GEN 是主动学习数据生成工作流中的关键配对。

## 协作模式
```
┌─────────────────────────────────────────────────────────┐
│                    DP-GEN 主动学习循环                     │
│                                                         │
│  ┌──────────┐    ┌──────────────┐    ┌───────────────┐  │
│  │ 初始数据  │───▶│ DP 训练      │───▶│ Ensemble 模型  │  │
│  │ (DFT)    │    │ (DeePMD-kit) │    │ (4个独立模型)  │  │
│  └──────────┘    └──────────────┘    └──────┬────────┘  │
│                                              │           │
│                    ┌─────────────────────────┘           │
│                    ▼                                     │
│             ┌──────────────┐                             │
│             │ LAMMPS MD    │  ← 探索步骤                 │
│             │ 候选构型生成  │                             │
│             └──────┬───────┘                             │
│                    ▼                                     │
│        ┌─────────────────────┐                           │
│        │ Model Deviation 计算 │  ← DeePMD-kit 核心组件    │
│        │ σ_low < σ < σ_high  │                           │
│        └──────────┬──────────┘                           │
│                   ▼                                      │
│         ┌──────────────────┐                             │
│         │ DFT 标注         │  ← VASP/CP2K 等             │
│         └────────┬─────────┘                             │
│                  ▼                                       │
│         ┌──────────────────┐                             │
│         │ 数据扩充 & 重训练 │──▶ 下一轮迭代               │
│         └──────────────────┘                             │
└─────────────────────────────────────────────────────────┘
```

## DP-GEN 中 DeePMD-kit 的角色
1. **训练**：DP-GEN 调用 `dp train` 训练 ensemble 模型（默认 4 个）。
2. **探索**：DP-GEN 调用 LAMMPS（`pair_style deepmd`）进行 MD 模拟，生成候选构型。
3. **筛选**：DP-GEN 使用 DeePMD-kit 的 `model_devi` 模块计算 model deviation，根据 σ_low/σ_high 阈值筛选候选构型。
4. **标注**：DP-GEN 调用 VASP/CP2K 对候选构型进行 DFT 计算。
5. **迭代**：DP-GEN 将新标注数据加入训练集，触发下一轮 `dp train`。

## 典型 DP-GEN 机器配置
- 训练机器：GPU 节点（2-8 张 GPU）
- MD 探索机器：GPU/CPU 节点
- DFT 标注机器：CPU 多核计算节点
- 调度器：Slurm/PBS/LSF
- 数据管理：DP-GEN 内部维护迭代目录结构：`iter.000/`, `iter.001/`, ...

## 规划要点
- Ensemble 模型数量的选择：4 个为经验值，更多模型增加训练代价但提高 deviation 可靠性。
- σ_low 和 σ_high 阈值设定需要根据体系化学键强度（例如共价键 ~eVA，离子键 ~0.1 eVA）校准。
- 主动学习迭代终止条件：model deviation 收敛（最大偏差不再超过 σ_high），或达到最大迭代次数。
- 初始训练集质量对主动学习效率至关重要，应覆盖目标相空间的关键区域。
- DPA-3 预训练模型可替代或加速主动学习中的初始模型训练，降低前几轮迭代的 DFT 计算需求。
