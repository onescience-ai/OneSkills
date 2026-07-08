# description
`mace_func_utils` 的规划决策用于确定 MACE 运行时需要输出哪些物理导数量，以及如何保证这些导数量的 autograd 路径、PBC 几何和 batch 聚合正确。它是从网络能量到可训练/可部署物理量的桥梁。

# when_to_use
- 需要开启或排查 forces、stress、virials、Hessian、edge forces 或 atomic stresses。
- 需要计算训练集均值、标准差、平均邻居数或力 RMS。
- 需要处理 LAMMPS/MLIAP 推理分支。
- 需要定位 `forces=None`、stress shape 错误、PBC 导数异常。
- 不用于选择 interaction block 或 loss 权重本身。

# inputs
- 输出需求：是否需要 force、stress、virial、Hessian、edge force。
- 数据字段：`positions`、`cell`、`edge_index`、`shifts`、`unit_shifts`、`batch`。
- 训练模式：是否需要保留高阶梯度。
- 物理约定：stress/virial 单位、符号、体积归一化方式。
- 资源限制：显存、二阶导预算、最大边数。
- 部署目标：普通推理、ASE、LAMMPS 或 MD。

# outputs
- 导数开关配置：`compute_force`、`compute_stress`、`compute_virials`、`compute_hessian`。
- 图准备策略：是否构造 symmetric displacement，是否启用 LAMMPS 分支。
- 统计量计划：avg neighbors、energy mean/std、force RMS。
- 验证结果：单 batch 能量-力梯度、stress/virial shape 和单位检查。
- 风险清单：梯度断裂、PBC 错位、二阶导成本过高。

# procedure
1. 确认任务目标是否真的需要 stress、virial 或 Hessian。
2. 检查数据 batch 是否包含 `positions`、`cell`、`shifts`、`unit_shifts` 和 `batch`。
3. 对需要 forces 的路径，确认 `positions` 在 forward 前未 detach 且可求导。
4. 对需要 stress/virial 的路径，启用 symmetric displacement 并检查 cell 体积。
5. 先在单 batch 上运行 `get_outputs`，检查所有输出 shape。
6. 将输出字段接入 loss 前，核验单位和符号。
7. 若用于部署，使用同一构型对训练模型与部署端输出做逐项比较。

# constraints
- 不在工具层改变数据单位或修正符号约定。
- 不默认开启 Hessian 或逐原子 stress。
- `cell`、`shifts` 和 `unit_shifts` 必须来自同一构图过程。
- LAMMPS 分支的原子数切片不应影响普通训练路径。
- 统计量必须基于训练集或明确指定的数据 split。

# next_phase_recommendation
- 为目标任务记录每个物理输出的单位、符号和 shape。
- 在训练前固定统计量计算脚本和结果。
- 对含应力任务，增加 stress/virial 数值 sanity check。
- 对部署任务，下一阶段建立 ASE/LAMMPS 一致性测试。

# fallback
- forces 为 None：检查 `positions.requires_grad` 和 energy 对 positions 的依赖路径。
- stress 异常：先关闭 stress，仅保留 forces；再逐步检查 displacement、cell 和单位。
- Hessian 内存爆炸：改用 loop、小 batch 或关闭 Hessian。
- PBC 输出异常：重新构图并检查 shifts 与 cell。
- LAMMPS 输出不一致：回退普通推理路径，逐项比较元素表、坐标、cell 和 batch。
