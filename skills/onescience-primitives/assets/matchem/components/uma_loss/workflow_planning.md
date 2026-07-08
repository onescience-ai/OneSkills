# description
`uma_loss` 的规划决策用于把 UMA 多任务训练目标转化为稳定的 loss 配置。它需要同时决定每个 property 的基础 loss、reduction、coefficient、mask、per-atom 归一化和 DDP 修正方式。

# when_to_use
- 需要配置 UMA energy、forces、stress 等任务 loss。
- 需要处理多任务 mask 或某些数据集缺失标签。
- 需要在 DDP 下保证不同 rank 原子数不一致时 loss 尺度正确。
- 需要排查 per-atom loss、L2 vector loss 或 NaN loss。
- 不用于生成 head 输出或构建图。

# inputs
- 任务列表：property 名称、目标张量 shape、是否按原子或按构型。
- head 输出 key 和 target key。
- `natoms`、`mult_mask`、normalizer 和 element references。
- 训练模式：单卡、DDP、graph/model parallel。
- 权重偏好：各任务 coefficient。
- 数据质量：NaN、缺失标签、无效 mask。

# outputs
- 每个任务的 loss 选择：MAE、MSE、PerAtomMAE、L2Norm。
- reduction 策略：mean、sum、per_structure。
- coefficient 配置。
- mask 与 DDP 修正策略。
- 验证计划：单 batch task loss、global sample count、NaN 检查。
- 风险清单：shape 不匹配、mask 错、natoms 错、normalizer 错。

# procedure
1. 为每个 task 确认输出 tensor shape 和目标物理意义。
2. 标量图级任务可选 MAE/MSE；能量 per-atom 任务考虑 `per_atom_mae`。
3. 向量力任务优先考虑 `l2norm` 或明确逐元素 MSE/MAE。
4. 若存在缺失标签，使用 `mult_mask` 并确认 mask shape。
5. DDP 训练使用 `DDPMTLoss` 或 `DDPLoss`，不要直接本地 mean。
6. 设置 coefficient，使不同任务梯度量级服务最终目标。
7. 首 batch 输出每个 task loss，检查 NaN、shape 和数值范围。

# constraints
- loss key 必须与 `uma_head` 输出和 task property 对齐。
- `natoms` 必须真实反映每个结构原子数。
- `mult_mask` 不能把所有样本屏蔽后仍按正常 loss 解释。
- normalizer/element reference 必须与 target 处理顺序一致。
- 频繁 NaN 不应只靠 `nan_to_num` 掩盖。

# next_phase_recommendation
- 建立 task-loss 映射表，记录 property、loss、reduction、coefficient、normalizer。
- 对多数据集训练统计每个 task 的有效 mask 比例。
- 在 DDP smoke test 中比较单卡与多卡首 batch loss。
- 与 head 输出联动检查 dataset-specific key。

# fallback
- shape mismatch：打印 input/target/mask shape，先关闭对应 task。
- loss 为 NaN：检查 target NaN/Inf、normalizer 和模型输出范围。
- DDP loss 偏差：确认全局样本数 all-reduce 和 `natoms`。
- per-atom loss 异常：检查 target 是否标量以及 `natoms` reshape。
- 多任务失衡：降低 dominant task coefficient，并验证下游指标。
