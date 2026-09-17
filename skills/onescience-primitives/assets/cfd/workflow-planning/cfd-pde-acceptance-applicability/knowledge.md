# PDE任务验收与适用域判定任务

## 适用范围
适用于PDE基础模型零样本预测场景的验收阶段，评估统计误差、关键物理约束、泛化能力和计算收益。不适用于仅评估统计误差而不考虑物理约束的场景。

## 输入
- 验收指标（相对L2、RMSE、守恒残差、边界误差）
- 相对误差门限（测试集放行阈值）
- 是否外推测试（测试域外工况）
- 预测结果（来自推理步骤）
- 真实标签（来自测试集）

## 输出
- evaluation.json（评估结果）
- worst_cases.csv（最差案例）
- applicability_report.md（适用域报告）
- PASS_REJECT_BLOCKED.txt（验收结论）

## 流程节点
按验收指标评价结果 → 报告逐变量误差、边界误差、守恒或方程残差、最差样本和推理成本 → 使用误差门限及任务物理门限给出PASS、REJECT或BLOCKED → 执行几何或工况外推测试并明确适用域

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 验收指标 | relative_L2, RMSE, conservation_residual, boundary_error | 场景需求书 | 统计和物理指标 |
| 相对误差门限 | 0.1 | 场景需求书 | 测试集放行阈值 |
| 是否外推测试 | true | 场景需求书 | 测试域外工况 |

## 边界与分流
- **统计与物理指标不同时报告**：必须同时报告统计和物理指标。
- **最差样本不可追溯**：必须记录最差样本信息。
- **结论不含适用域限制**：必须明确适用域和复核建议。

## 质量检查
- 统计与物理指标同时报告
- 最差样本可追溯
- 结论含适用域限制与复核建议

## 回退策略
- 验收失败：分析失败原因，调整模型或数据，重新训练。
- 适用域过窄：扩展训练数据覆盖范围，引入领域自适应技术。

## 资源召回建议
当用户需要进行PDE基础模型零样本预测的验收时召回本卡片。配套资源包括：评估脚本、可视化工具、报告生成工具。

## 补充证据（开源文档/用户自有，可选）
无

## 证据来源
[1] Zebra: In-Context Generative Pretraining for Solving Parametric PDEs, Louis Serrano et al., arXiv, 2024, DOI: 10.48550/arXiv.2410.03437
[2] Physics-informed Temporal Alignment for Auto-regressive PDE Foundation Models, 2024
[3] Zero-shot forecasting of chaotic systems, 2024
[4] Multiple Physics Pretraining for Spatiotemporal Surrogate Models, 2024
[5] MetaPhysiCa: Improving OOD Robustness in Physics-informed Machine Learning, 2024
[6] FLUID-LLM: Learning Computational Fluid Dynamics with Spatiotemporal-aware Large Language Models, Max Zhu et al., arXiv, 2024, DOI: 10.48550/arXiv.2406.04501