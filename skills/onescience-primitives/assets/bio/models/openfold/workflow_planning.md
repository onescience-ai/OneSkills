# description

OpenFold 的规划知识用于判断何时把蛋白序列结构预测任务交给 AF2-style 折叠模型，并把 FASTA、MSA/template、checkpoint、preset、资源约束和下游验证组织成可执行步骤。

# when_to_use

- 用户明确提到 OpenFold、AlphaFold2 风格结构预测、MSA/template 驱动折叠、monomer/multimer preset 或 recycling。
- 用户有蛋白 FASTA、预计算 OpenFold feature dict，或愿意调用数据库和 alignment 工具生成特征。
- 用户需要评估 ProteinMPNN 设计序列、天然蛋白序列或突变体的三维结构和置信度。
- 当 `workflow_type=protein_design_to_structure_validation` 且当前阶段需要 AF2/OpenFold 风格 MSA/template 复核时，OpenFold 可作为 SimpleFold 后的高置信度结构验证器。
- 若端到端任务缺少 MSA/template/feature 资产且只需要快速单体初筛，优先 SimpleFold；若需要复合物、核酸或配体，优先 Protenix/AlphaFold3。
- 不在用户只要求生成骨架时使用；骨架生成优先 RFdiffusion。
- 不在用户要求蛋白-核酸-配体复合物时使用；复合物结构优先 Protenix。

# inputs

- 用户目标：结构预测、设计序列验证、突变体结构比较、批量候选筛选。
- 生物输入：FASTA、OpenFold feature dict、MSA、template、序列长度、链信息。
- 模型选择：`config_preset`、checkpoint、是否使用 template、recycle 设置、设备。
- 资源输入：数据库路径、alignment/template 工具路径、输出目录、显存限制。
- 上下游输入：上游可来自天然序列、ProteinMPNN 设计序列或人工突变序列；下游可进入结构筛选、复合物分析或实验候选排序。
- 端到端上游产物：ProteinMPNN FASTA、SimpleFold 初筛结果、候选 ID，或用户提供的设计序列；需要额外补齐 OpenFold feature dict、MSA/template 或数据库工具。

# outputs

- 召回决策：是否使用 OpenFold、使用 `structure_prediction` 还是 `design_validation`。
- 执行计划：入口脚本、输入目录、数据库/checkpoint 绑定、preset、资源策略和输出目录。
- 结果产物：预测结构、置信度指标、中间 pickle、日志、失败诊断。
- 下游交接：将 PDB、置信度指标、中间 feature/result 文件、候选 ID 和失败诊断交给 ranking/report；复合物候选再转 Protenix/AlphaFold3。

# procedure

1. 判断用户目标是否为蛋白序列到结构，且是否需要 AF2-style MSA/template 协议。
2. 若是端到端 workflow，确认本阶段是 `af2_style_validation` 或 `high_confidence_monomer_review`，且已有 FASTA/feature 与 MSA/template 资产。
3. 区分输入来源：普通 FASTA 走特征生成；预计算 OpenFold feature dict 走直接推理；设计序列先规范 FASTA header。
4. 选择运行模式：单体/多聚体、template 开关、recycle/preset、是否批量候选验证。
5. 做执行前检查：数据库、alignment 工具、checkpoint、`max_template_date`、输出目录、GPU 显存和 feature recycling 维度。
6. 生成命令或 API 调用计划，并记录输入、参数、资源和预期输出。
7. 解析 observation：PDB 是否存在、置信度是否可读、日志是否显示数据库/feature/显存错误。
8. 根据结果衔接下游：高置信度结构进入候选排序；低置信度结构尝试改 MSA/template、换 SimpleFold/ESMFold 对照，或回到序列设计阶段。

# constraints

- 只处理蛋白序列结构预测，不承担 DNA/RNA/配体复合物建模。
- `AlphaFold.forward` 必须接收 OpenFold feature dict，不能直接接收 FASTA 字符串。
- monomer/multimer、template、checkpoint 和 feature pipeline 必须匹配。
- 设计流程中 OpenFold 是结构验证或筛选环节，不负责从头生成骨架或设计序列。
- 本卡只声明 AF2/OpenFold 验证 stage contract；未来其它端到端 workflow 可复用 FASTA/feature -> structure/confidence 的输入输出字段。

# next_phase_recommendation

- 若结构预测置信度高，进入结构质量筛选、结合界面分析或实验候选排序。
- 若输入来自 RFdiffusion 设计骨架，应先用 ProteinMPNN 生成序列，再用 OpenFold 验证序列可折叠性。
- 若用户需要复合物、核酸或配体，改用 Protenix。
- 若数据库不可用且用户接受快速单序列近似，可转 SimpleFold 或 ESMFold。

# fallback

- 数据库或 alignment 工具不可用：使用预计算 OpenFold 特征，或切换到单序列折叠模型。
- 显存不足：减少 batch、减少 template/MSA、缩短候选列表、启用低内存策略或改用更小模型。
- feature 报错：回到 OpenFold 特征流水线补齐字段，不在模型输入中随意填假特征。
- 结构置信度低：尝试更完整 MSA/template、不同 preset，或把候选退回 ProteinMPNN/RFdiffusion 重新设计。
