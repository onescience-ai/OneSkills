# description
`mace_loss` 的规划决策用于把材料势函数任务目标转化为可训练的多物理量损失配置。它要求在 energy、forces、stress、virials、dipole 之间选择监督项和权重，并保证字段、单位、归一化和 DDP 归约一致。

# when_to_use
- 需要配置 MACE 训练或 fine-tuning loss。
- 需要决定能量、力、应力、virial 或偶极是否参与训练。
- 需要排查训练 loss 异常、DDP loss 不一致或 per-atom 标准化错误。
- 需要为新增 property 增加监督目标。
- 不用于从能量计算 forces，也不用于选择径向 cutoff。

# inputs
- 任务目标：能量精度、力精度、应力精度、MD 稳定性、偶极性质。
- 数据字段：`energy`、`forces`、`stress`、`virials`、`dipole`、权重字段。
- 单位和符号：能量/力/stress/virial 的物理约定。
- batch 信息：`ptr`、`batch`、每图原子数。
- 训练模式：单卡或 DDP，多头或单头。
- 模型输出：prediction dict 的字段和 shape。

# outputs
- loss 类选择：如 `WeightedEnergyForcesLoss`、`WeightedEnergyForcesStressLoss`、`UniversalLoss`。
- 权重配置：energy/forces/stress/virials/dipole 子项系数。
- 字段契约：reference 与 prediction 的 key 对齐表。
- 验证计划：首 batch loss 分项、DDP 归约、单位和 shape 检查。
- 风险清单：字段缺失、权重失衡、stress 符号错、per-atom 归一化错。

# procedure
1. 明确训练目标是否需要 E、F、S、virial、dipole 中的哪些监督项。
2. 抽样检查 batch 标签字段、shape、单位和符号。
3. 根据任务选择 loss 类；先用简单 E/F loss 跑通，再加入 stress 或 virial。
4. 设置权重：力主导任务提高 `forces_weight`，力学任务加入 `stress_weight`。
5. 单 batch 打印 loss 分项，确认数量级合理。
6. DDP 训练时确认 `reduce_loss` 生效，避免 rank 间原子数差异造成偏差。
7. 用验证集和下游 MD/relaxation 检查权重是否真的服务任务目标。

# constraints
- 不用 loss 层修正单位或字段名混乱。
- 不把 `stress` 与 `virials` 混用，除非明确转换关系。
- 不用普通 `.mean()` 替代分布式归约逻辑。
- 多头 loss 必须与 head id 和输出 key 对齐。
- 训练 loss 不是唯一评估标准。

# next_phase_recommendation
- 为每个数据集记录 loss 权重和字段单位。
- 建立首 batch loss 分项检查。
- 对含 stress/virial 的任务增加独立物理 sanity check。
- 对 MD 任务增加能量漂移、力异常值和结构稳定验证。

# fallback
- loss 为 NaN：先关闭 stress/virial/Hessian，只保留 E/F，检查标签异常。
- force loss 过大：检查力单位、符号、坐标单位和模型输出 shape。
- energy 偏移大：检查 E0s、per-atom 归一化和元素表。
- DDP loss 不一致：检查 `reduce_loss` 和每 rank batch 原子数。
- 新 property 训练失败：先确认 prediction/reference key，再加权接入组合 loss。
