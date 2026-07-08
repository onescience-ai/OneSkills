# description
`uma_graph_compute` 的规划决策用于确定 UMA 运行时如何从结构构造近邻图。它需要在物理截断、邻居上限、PBC 策略、训练/推理一致性和显存边数之间做明确取舍。

# when_to_use
- 需要配置 UMA on-the-fly graph。
- 需要调整 cutoff、max_neighbors 或 radius PBC 实现版本。
- 需要处理周期/非周期结构、calculator 推理或外部图输入。
- 需要排查 edge_index、edge_distance、cell_offsets 或邻居数异常。
- 不用于修改 backbone block 或 head。

# inputs
- 结构字段：`pos`、`cell`、`natoms`、`pbc`。
- 图参数：cutoff、max_neighbors、strict neighbor、radius_pbc_version。
- 运行策略：`otf_graph`、`always_use_pbc`、外部图字段是否存在。
- 数据类型：周期晶体、非周期分子、混合 batch。
- 资源限制：边数、显存、推理延迟。

# outputs
- 图构建策略：on-the-fly 或外部预构图。
- 参数建议：cutoff、max_neighbors、PBC 版本和 strict 策略。
- 字段契约：edge_index、edge_distance、edge_distance_vec、cell_offsets、neighbors。
- 验证计划：边数统计、零距离过滤、PBC 位移 sanity check。
- 风险清单：zero cell、混合 PBC、训练推理图策略不一致、邻居截断过强。

# procedure
1. 判断数据是否需要 PBC；周期体系确认 cell 有效。
2. 选择 cutoff，优先与预训练或训练配置保持一致。
3. 根据体系密度设置 `max_neighbors`，统计是否发生频繁截断。
4. 选择 `radius_pbc_version`，用小 batch 比较边数和距离输出。
5. 决定是否 `otf_graph`；若关闭，确认外部图字段完整。
6. 对单 batch 检查 `edge_index`、`edge_distance`、`edge_distance_vec` 和 `neighbors`。
7. 确认训练、验证、推理和 calculator 使用相同构图策略。

# constraints
- cutoff 与 backbone 径向层必须一致。
- `max_neighbors` 不应过小到截断关键相互作用。
- PBC 与 cell 必须同源且逐结构匹配。
- 混合 PBC batch 需要显式策略，不应默认假设全周期。
- 外部图字段不能和当前坐标/cell 脱节。

# next_phase_recommendation
- 记录边数分布和 max_neighbors 截断比例。
- 对目标数据集建立 graph smoke test。
- 在 calculator 推理前比较训练和推理构图输出。
- 对非周期分子单独配置 pbc 和 zero cell 处理策略。

# fallback
- 构图失败：先用单结构 batch 验证 cell、pbc 和 cutoff。
- 边数爆炸：降低 cutoff 或 max_neighbors，检查结构密度和单位。
- 邻居截断过强：提高 max_neighbors 或关闭严格截断做对照。
- zero cell 错误：非周期体系关闭 PBC，周期体系修复 cell。
- 推理误差异常：对同一结构比较训练构图和推理构图字段。
