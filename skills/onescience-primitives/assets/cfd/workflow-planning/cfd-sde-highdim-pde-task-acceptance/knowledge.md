# Task Acceptance & Applicability Assessment for Stochastic PDE

## 适用范围
本任务面向随机微分方程（SDE）与高维偏微分方程（PDE）求解的任务验收阶段，评估统计误差、关键物理约束、泛化能力和计算收益，给出PASS、REJECT或BLOCKED结论。适用于所有需要物理信息PDE求解的验收评估场景，域外工况需经传统CFD复核后方可工程部署。**不得仅凭平均误差宣称工程可用**。

## 输入
- {METRICS}：验收指标列表（relative_L2, PDE_residual, boundary_error, conservation_error），必填
- {MAX_RELATIVE_L2}：相对误差门限（测试集放行阈值），可选
- {RUN_OOD_TEST}：是否外推测试（测试域外工况），可选

## 输出
- evaluation.json：评估结果
- worst_cases.csv：最差样本清单
- applicability_report.md：适用域报告
- PASS_REJECT_BLOCKED.txt：验收结论

## 流程节点
```
1. 读取s04解场与残差 → 2. 计算统计误差（相对L2误差）
→ 3. 评估物理约束（PDE残差、边界误差、守恒误差）
→ 4. 识别最差样本 → 5. 计算推理成本
→ 6. 若RUN_OOD_TEST则执行外推测试 → 7. 判定PASS/REJECT/BLOCKED
→ 8. 生成适用域报告
```

## 关键参数

### 通用判据（方法层，同类体系可参考）

| 参数 | 判据 | 说明 |
|------|------|------|
| 统计与物理指标同时报告 | 缺一不可 | 不能仅凭统计误差判定 |
| 最差样本可追溯 | 有唯一标识与详细分析 | 支持后续改进 |
| 适用域限制明确 | 结论含适用域范围 | 不得泛化到域外工况 |
| 复核建议 | 域外工况需CFD复核 | 工程部署安全 |
| 外推测试 | 几何或工况外推 | 验证泛化能力 |

### 校准数值（场景专属值，供量级校准）
以下数值来自 CFD_S046 场景，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认MAX_RELATIVE_L2 | 0.1 | 场景需求书 | 测试集放行阈值（10%） |
| 默认验收指标 | relative_L2, PDE_residual, boundary_error, conservation_error | 场景需求书 | 四项指标缺一不可 |

## 判定标准

| 结论 | 条件 |
|------|------|
| PASS | 所有指标满足门限；最差样本误差可接受；适用域明确 |
| REJECT | 任一关键指标超门限；物理约束不满足；最差样本不可接受 |
| BLOCKED | 缺少必填输入；数据不可用；验证受限（无独立解对照） |

## 边界与分流
- **缺少必填指标**：返回BLOCKED
- **无独立解对照**：标记为"验证受限"，仅报告统计误差
- **域外工况失败**：明确标记为不适用，建议CFD复核
- **最差样本不可接受**：REJECT，需改进模型或数据

## 质量检查
- 统计误差计算正确性
- 物理约束满足性验证
- 最差样本追溯性
- 适用域报告完整性
- 验收结论合理性

## 回退策略
- 验收失败：分析失败原因，改进模型/数据/训练策略
- 适用域过窄：考虑增加训练数据、调整模型架构
- 推理成本过高：考虑模型压缩、近似推理

## 资源召回建议
当遇到以下需求时召回本卡片：
- 物理信息PDE求解结果的验收评估
- 适用域判定与工程部署决策
- 模型泛化能力评估

配套卡片：cfd-sde-highdim-pde-equation-solve-residual（方程求解），cfd-stochastic-pde-physical-network-solver（工作流总览）

## 证据来源
[1] Physics-Informed Inference Time Scaling for Solving High-Dimensional Partial Differential Equations, 2024
[2] Aerodynamic force reconstruction using physics-informed Gaussian processes, arXiv:2605.22111, 2025
[3] UrbanGraph: Physics-Informed Spatio-Temporal Dynamic Heterogeneous Graphs for Urban Microclimate Prediction, 10.1016/j.buildenv, 2024
