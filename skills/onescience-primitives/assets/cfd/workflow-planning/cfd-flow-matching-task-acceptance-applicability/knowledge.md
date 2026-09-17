# Flow Matching 任务验收与适用域判定

## 适用范围

本任务评估 Flow matching 概率代理的综合性能，给出 PASS、REJECT 或 BLOCKED 判定。适用于流匹配概率代理构建流程的第五阶段（最终阶段）。核心原则：不得仅凭平均误差宣称工程可用，必须同时报告统计误差、物理约束、最差样本和适用域限制。域外工况须经 CFD 复核。

## 输入

- 验收指标列表（{METRICS}，默认 distribution_distance、diversity、physics_residual、coverage）
- 相对误差门限（{MAX_RELATIVE_L2}，默认 0.1）
- 外推测试标志（{RUN_OOD_TEST}，默认 true）
- 生成样本与物理筛选结果（来自阶段 4）

## 输出

- evaluation.json（逐变量误差、边界误差、守恒/方程残差、推理成本）
- worst_cases.csv（最差样本列表与详细信息）
- applicability_report.md（适用域报告，含工况范围限制与复核建议）
- PASS_REJECT_BLOCKED.txt（最终判定）

## 流程节点

1. 加载阶段 4 的生成样本与物理筛选结果
2. 计算逐变量统计误差（分布距离、覆盖度）
3. 计算边界误差与守恒/方程残差
4. 识别最差样本并记录详细信息
5. 评估推理成本（时间、内存）
6. 若{RUN_OOD_TEST}=true，执行几何或工况外推测试
7. 综合评估给出 PASS / REJECT / BLOCKED 判定
8. 生成适用域报告，明确工况范围限制
9. 输出验收报告与判定文件

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| MAX_RELATIVE_L2 | 0.1 | [场景需求书] | 测试集放行阈值 |
| RUN_OOD_TEST | true | [场景需求书] | 默认执行外推测试 |
| 验收指标 | distribution_distance, diversity, physics_residual, coverage | [场景需求书] | 默认指标集 |

## 边界与分流

- 平均误差达标但最差样本不合格：REJECT，标注最差样本工况
- 物理约束不满足：REJECT，说明具体违反的物理定律
- 域外工况性能急剧下降：明确标注适用域边界，建议 CFD 复核
- 推理成本过高：标注推理时间与资源消耗，评估工程可行性
- 所有指标达标且域外测试通过：PASS

## 质量检查

- 统计与物理指标同时报告
- 最差样本可追溯
- 结论含适用域限制与复核建议
- 不得仅凭平均误差宣称工程可用

## 回退策略

- REJECT → 回退阶段 3 重新训练，或 BLOCKED 并报告
- BLOCKED → 停止流程，报告所有失败原因
- 适用域不明确 → 补充更多外推测试

## 资源召回建议

当用户需要对 Flow matching 概率代理进行最终验收或适用域评估时召回本卡片。前置步骤：cfd-flow-matching-conditional-sampling-physics-filter。可参考 cfd-diffusion-stochastic-pde-probability-prediction-scenario 了解同类概率代理的验收对比。

## 证据来源

[1] Switched Flow Matching: Eliminating Singularities via Switching ODEs, 2024
[2] Physics vs Distributions: Pareto Optimal Flow Matching with Physics Constraints, 2024
[3] Dflow-SUR: Enhancing Generative Aerodynamic Inverse Design using Differentiation Throughout Flow Matching, arXiv:2512.08336, 2025
[4] GeoFunFlow-3D: A Physics-Guided Generative Flow Matching Framework for High-Fidelity 3D Aerodynamic Inference over Complex Geometries, arXiv:2604.23350, 2026
[5] Physics-Guided Generative Surrogates for Parametric Rarefied Flows with Neural-Field Auto-Decoders: A Pipeline-Level Study of Flow Matching and Diffusion, arXiv:2608.25454, 2026
