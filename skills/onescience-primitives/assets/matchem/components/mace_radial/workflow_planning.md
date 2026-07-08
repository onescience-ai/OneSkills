# description
`mace_radial` 的规划决策用于确定 MACE 边距离如何被表达、截断和短程修正。核心不是单独选择一个基函数，而是同时约束数据单位、构图 cutoff、径向基规模、ZBL 是否启用以及 checkpoint 兼容性，确保训练、推理和 MD 的局部相互作用语义一致。

# when_to_use
- 需要设置或排查 MACE 的 `r_max`、径向基数量和 cutoff 平滑。
- 需要判断是否启用 ZBL 短程排斥。
- 需要处理高压、碰撞、短距离异常或 MD 稳定性问题。
- 需要检查 foundation model fine-tuning 中 cutoff 是否可改。
- 不用于选择 loss 权重或模型 head。

# inputs
- 数据单位和坐标尺度。
- 构图 cutoff、`r_max`、`max_neighbors` 或等价邻域策略。
- 径向配置：`radial_type`、`num_bessel`、`num_polynomial_cutoff`、`distance_transform`。
- checkpoint 信息：预训练模型的 cutoff 和径向基类型。
- 短程样本分布：最小原子间距、碰撞构型、MD 失败样本。

# outputs
- 径向配置建议：基函数类型、基数量、cutoff 阶数、是否可训练。
- cutoff 兼容性判断：是否可沿用 checkpoint，是否需要重新构图或重训。
- ZBL 决策：是否启用 pair repulsion 及需要验证的元素映射。
- 验证计划：边距离直方图、短距离稳定性、MD smoke test。

# procedure
1. 读取数据坐标单位，确认 Angstrom 语义是否成立。
2. 统计目标体系边距离分布和最大邻居数。
3. 若加载 foundation checkpoint，优先沿用其 `r_max` 与径向基配置。
4. 若从头训练，根据相互作用范围选择 `r_max`，再匹配构图 cutoff。
5. 选择径向基数量，先使用 demo 稳定值，再按误差和资源调整。
6. 判断短程异常是否明显；如存在高能碰撞或 MD 崩溃，评估 `ZBLBasis`。
7. 做单 batch forward 和短 MD/relaxation 验证。

# constraints
- `r_max`、构图 cutoff 和数据单位必须一致。
- 改径向基类型通常不能直接复用旧径向权重。
- ZBL 元素映射必须与 `node_attrs` 完全一致。
- 不应只通过增大 cutoff 解决所有精度问题，边数增长会放大显存和时间成本。

# next_phase_recommendation
- 将边距离统计和 cutoff 选择写入数据卡。
- 对 foundation fine-tuning，先做不改 cutoff 的 baseline。
- 对 MD 任务，增加短程异常构型验证集。
- 若要改变 cutoff，下一阶段同步更新 datapipe、模型配置和 checkpoint 加载策略。

# fallback
- cutoff 不兼容：回退到 checkpoint 原始 `r_max`。
- 显存不足：降低 cutoff 或 batch size，检查邻居数分布。
- 短程不稳定：启用 ZBL 或补充短距离训练样本。
- 元素映射异常：重新生成元素表和 one-hot，避免在径向层硬修。
- 距离变换导致发散：关闭 transform，恢复标准径向基 baseline。
