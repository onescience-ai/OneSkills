# description
`uma_escn_moe` 的规划决策知识用于指导 agent 在 UMA 多域材料势任务中判断是否需要 MoE/MOLE 专家路由、如何配置专家数量和替换层、如何准备 dataset/charge/spin/组成路由输入，以及如何在训练后选择动态 MoE 推理或合并为普通 eSCNMDBackbone。决策核心是先确认普通 `uma_escn_md` 是否足够，再在多数据域、多任务、强异构组成或 dataset-specific 输出需求明确时启用该原语。

# when_to_use
- 目标任务包含多个 dataset、多个材料域或多个任务分布，普通 UMA backbone 表现冲突明显。
- 需要按 charge、spin、dataset 或元素组成动态调节 backbone 参数。
- 需要在 OC20、OMAT、OMOL、自定义分子/晶体/表面数据之间共享模型，同时保留域特异适配能力。
- 需要配合 `DatasetSpecificMoEWrapper` 或 dataset-specific head 进行多域输出。
- 计划训练后对某个固定数据上下文合并专家权重，用普通 eSCNMDBackbone 做部署。

不优先使用：

- 单一数据域、样本量较小、普通 `escnmd_backbone` 已能稳定收敛。
- 数据没有可靠 dataset、charge、spin 或组成信息，无法形成稳定路由。
- 主要风险来自数据字段、单位、PBC 或标签质量，而不是模型容量不足。
- 推理部署需要完全动态适配所有数据域，但资源预算不允许额外专家计算。

# inputs
- 任务类型：multi-domain fine-tuning、energy-only、EF、EFS、batch inference、relaxation/MD 或 fixed-context deployment。
- 数据域信息：dataset 名称列表、每个域的样本量、元素覆盖、charge/spin 分布、PBC 类型。
- 标签与统计：energy/forces/stress 字段、单位、`elem_refs`、`normalizer_rmsd`、loss/metric。
- 基础模型信息：UMA checkpoint、`Jd.pt`、`dataset_list`、基础 eSCNMD 结构参数。
- MoE 配置候选：`num_experts`、`layers_moe`、`moe_type`、`moe_dropout`、`use_composition_embedding`、`moe_single`。
- head 配置：普通 head、dataset-specific head 或 MoE wrapper。
- 资源约束：显存、训练时长、batch size、最大边数、是否需要部署合并。
- 验证信号：整体误差、分 dataset 误差、专家利用率、专家系数方差、MD/relaxation 稳定性。

# outputs
- 选型结果：使用 `uma_escn_moe`、退回 `uma_escn_md`，或转向其他材料势模型。
- MoE 配置：专家数量、专家化层范围、替换类型、路由输入和归一化策略。
- 数据契约：dataset_list、dataset 字段、charge/spin 策略、composition embedding 是否启用、PBC 分流策略。
- 训练配置：checkpoint、head、tasks_list、elem_refs、normalizer、loss 权重、学习率、batch size。
- 监控计划：专家系数均值/方差、分域验证误差、无边图比例、PBC 断言、下游稳定性。
- 部署策略：保留动态 MoE，或基于代表性 data 调用 `merge_MOLE_model` 生成固定普通 backbone。
- 风险清单：专家塌缩、过拟合、路由字段缺失、checkpoint 不兼容、合并上下文过窄、显存不足。

# procedure
1. 先建立普通 `uma_escn_md` baseline，确认数据字段、PBC、Jd、checkpoint、head 和 loss 均可运行。
2. 分析 baseline 的分域误差；只有当误差呈明显 dataset/组成/charge/spin 相关冲突时，启用 MoE。
3. 选择路由输入：
   - dataset/charge/spin 差异为主：使用默认 `csd_mixed_emb`。
   - 元素组成差异显著：设置 `use_composition_embedding=true`。
4. 选择专家规模：
   - 初始使用 `num_experts=4` 或 `8`。
   - 数据少或不稳定时减少专家。
   - 多域差异强且数据充足时再增加专家。
5. 选择专家化范围：
   - 默认 `moe_type=so2`。
   - 显存紧张或想降低风险时用 `layers_moe` 只专家化后几层。
   - 只有明确实验需要时才尝试 `all` 或 `notso2`。
6. 绑定数据统计：确保 `dataset_name`、`elem_refs`、`normalizer_rmsd`、head、tasks_list 同源。
7. 生成 Hydra override 或 YAML，显式写入 `escnmd_moe_backbone`、专家参数和基础 backbone 参数。
8. 运行小 batch smoke test，检查 `expert_mixing_coefficients`、`mole_sizes`、head 输出和 loss。
9. 正式训练时监控整体指标和分 dataset 指标，同时观察专家系数均值/方差，防止专家塌缩。
10. 若需要部署固定模型，选择代表性 data 调用 `merge_MOLE_model`，并对合并前后同一 batch 输出做一致性检查。
11. 对 MD/relaxation 使用场景，额外检查能量漂移、异常力、结构收敛和不同域的稳定性。

# constraints
- 不要用 MoE 掩盖数据字段、单位、PBC 或标签错误；这些问题必须先在普通 UMA baseline 中解决。
- `dataset_list` 必须覆盖所有训练和推理 dataset。
- `num_experts` 必须与数据量和域数量匹配，不能盲目增大。
- `mole_type` 必须为 `so2`、`so2m0`、`all`、`notso2` 之一。
- 需要 `merge_MOLE_model` 时必须使用 `mole_type=so2`。
- 合并模型只适合固定路由上下文；跨 dataset 动态泛化时应保留 MoE 模型。
- `moe_layer_type=dgl` 需要额外扩展支持，默认规划使用 `pytorch`。
- `use_composition_embedding=true` 时，元素覆盖和 batch 映射必须可靠。
- 同一 batch 的 PBC 仍需全 true 或全 false，混合 PBC 应先拆分。

# next_phase_recommendation
- 为每个 dataset 建立分域数据卡，记录元素分布、charge/spin、PBC、标签单位和统计量来源。
- 先训练 `num_experts=4/8`、`moe_type=so2`、部分层专家化的轻量配置，再扩展到更多层或更多专家。
- 增加专家利用率报告，记录每个 dataset 的专家系数均值、方差和路由分布。
- 对 dataset-specific head 与 MoE backbone 做消融，区分 head 不足和 backbone 表征冲突。
- 若计划部署合并模型，为每个部署域准备代表性合并样本和一致性验证脚本。
- 在 MD/relaxation 场景中加入分域短轨迹稳定性评估，避免只看静态 MAE。

# fallback
- 专家系数塌缩：增加 dropout、降低学习率、减少专家数，或限制 `layers_moe`。
- 显存不足：降低 batch size、num_experts、专家化层数，优先保持基础物理字段正确。
- MoE 替换失败：检查 `moe_type`、`moe_layer_type` 和目标层是否存在；先回退 `moe_type=so2`。
- `merge_MOLE_model` 失败：确认 `mole_type=so2`，并提供包含 atomic_numbers、batch、charge、spin、dataset 的代表性 data。
- 合并后跨域效果差：保留动态 MoE，不使用固定合并模型跨域部署。
- 分 dataset 误差没有改善：退回普通 `uma_escn_md`，优先检查数据统计、head 配置和 loss 权重。
- 路由字段缺失：补齐 dataset、charge、spin 或关闭 composition embedding；不要用错误常数掩盖真实域差异。
- 基础 forward 失败：按 UMA 基础风险排查 `Jd.pt`、PBC、无边图、预计算图字段和 checkpoint。
