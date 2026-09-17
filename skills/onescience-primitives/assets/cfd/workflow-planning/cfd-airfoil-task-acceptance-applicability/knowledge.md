# 任务验收与适用域判定任务

## 适用范围
本任务适用于评估统计误差、关键物理约束、泛化能力和计算收益，确定模型是否可用及适用范围。

## 输入
- 验收指标列表
- 相对误差门限
- 是否外推测试选项
- 推测结果
- 测试集清单
- 数据契约

## 输出
- 评估报告（evaluation.json）
- 最差样本列表（worst_cases.csv）
- 适用域报告（applicability_report.md）
- 验收结论（PASS_REJECT_BLOCKED.txt）

## 流程节点
1. 计算统计误差指标（relative_L2, RMSE）
2. 计算物理约束指标（conservation_residual, boundary_error）
3. 分析最差样本
4. 计算推理成本
5. 执行几何或工况外推测试
6. 明确适用域
7. 给出PASS、REJECT或BLOCKED结论

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 验收指标 | relative_L2, RMSE, conservation_residual, boundary_error | [场景需求书] | 统计与物理指标 |
| 相对误差门限 | 0.1 | [场景需求书] | 默认阈值 |
| 外推测试 | true | [场景需求书] | 默认执行 |

## 边界与分流
- 统计误差超限：分析失败原因，可能需调整模型或数据。
- 物理约束违反：检查模型或数据，可能需引入物理约束。
- 最差样本误差过大：分析失败原因，可能需调整模型或数据。
- 域外工况：执行外推测试并明确适用域，需CFD复核。

## 质量检查
- 统计与物理指标同时报告。
- 最差样本可追溯。
- 结论含适用域限制与复核建议。

## 回退策略
- 验收不通过：分析评估报告，调整模型或数据。
- 适用域过窄：重新收集数据或调整模型架构。
- 域外工况：需CFD复核，不得直接信任模型预测。

## 资源召回建议
当用户需要进行任务验收与适用域判定时，可召回本任务卡片。配套资源包括：
- 统计误差计算工具
- 物理约束检查工具
- 适用域分析工具
- 报告生成工具

## 证据来源
[1] A Kernel-based Resource-efficient Neural Surrogate for Multi-fidelity Prediction of Aerodynamic Field, arXiv:2512.10287, 2025
[2] AFBench_ A Large-scale Benchmark for Airfoil Design, arXiv:1411.1784, 2014
[3] Airfoil optimization using Design-by-Morphing with minimized design-space dimensionality, arXiv:2510.16020, 2025
[4] Predictive Criteria for Electrospray-Assisted Droplet Dynamics in Aerodynamic Flow Fields, arXiv:2509.22676, 2025
[5] AeroJEPA_ Learning Semantic Latent Representations for Scalable 3D Aerodynamic Field Modeling, arXiv:2605.05586, 2026
[6] AirfoilGen_ A valid-by-construction and performance-aware latent diffusion model for airfoil generation, arXiv:2605.20303, 2026