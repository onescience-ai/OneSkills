# description

用于规划 MSA 表征中的行列轴向注意力，把同源序列维和 residue 维的信息分开聚合。

# when_to_use

- 输入包含 MSA，而不是单条序列。
- 需要蛋白家族同源信息支持结构或接触建模。
- 需要复用 ESM-MSA 风格模块。

# inputs

- MSA activation 维度。
- MSA 行数、列数和 mask。
- 是否存在显存限制。

# outputs

- row/column attention 调用顺序。
- 分块策略。
- 与 MSA transformer 层的连接建议。

# procedure

1. 确认输入布局为 MSA 轴向布局。
2. 检查 row/column mask 与 padding。
3. 根据 token 数决定是否分块。
4. 将输出接入后续 transformer 或 contact head。

# constraints

- 不适用于单个分子图。
- 大 MSA 内存成本高。
- 维度顺序错误会直接失败。

# next_phase_recommendation

若任务无 MSA，转用 ESM 普通 transformer；若任务需要结构预测，可继续接 contact head 或结构模块。

# fallback

当 MSA 过大时，裁剪同源序列、分块计算或退回单序列 ESM 表征。
