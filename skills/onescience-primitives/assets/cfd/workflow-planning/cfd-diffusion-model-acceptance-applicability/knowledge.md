# 任务验收与适用域判定

## 适用范围

适用于物理信息扩散模型流场分布生成任务的最终验收阶段。按统计与物理指标评估生成结果，给出 PASS/REJECT/BLOCKED 结论，并通过几何或工况外推测试明确模型的适用域边界。该方法确保模型在工程应用中的可靠性与可追溯性。

## 输入

- {METRICS}（必填）：验收指标列表
- {MAX_RELATIVE_L2}（可选）：相对误差门限，默认 0.1
- {RUN_OOD_TEST}（可选）：是否外推测试，默认 true
- s04 产出的 generated_samples/、physics_filter.json、distribution_metrics.json

## 输出

- evaluation.json：完整评估结果（逐变量误差、边界误差、守恒残差、方程残差）
- worst_cases.csv：最差样本记录（含条件、残差、错误模式）
- applicability_report.md：适用域报告（几何/工况覆盖范围、外推测试结论）
- PASS_REJECT_BLOCKED.txt：最终验收结论

## 流程节点

1. 读取 s04 产出的样本与筛选结果
2. 计算逐变量统计误差（相对 L2、MAE、RMSE）
3. 计算边界残差（边界条件满足程度）
4. 计算守恒残差（质量、动量、能量守恒误差）
5. 计算方程残差（Navier-Stokes 方程满足程度）
6. 识别最差样本并记录错误模式
7. 计算推理成本（时间、内存）
8. 若 {RUN_OOD_TEST}=true，执行几何或工况外推测试
9. 按 {MAX_RELATIVE_L2} 及物理门限给出 PASS/REJECT/BLOCKED
10. 生成适用域报告与复核建议

## 关键参数

### 通用判据

| 参数 | 说明 | 来源 |
|------|------|------|
| 统计与物理同时报告 | 不得只报告统计误差而忽略物理约束 | [场景需求书 s05] |
| 最差样本可追溯 | 最差样本的条件、残差、错误模式完整记录 | [场景需求书 s05] |
| 适用域限制 | 结论须含几何/工况覆盖范围与限制 | [场景需求书 s05] |
| 复核建议 | 域外工况须建议 CFD 复核 | [场景需求书 s05] |
| 禁止平均误差宣称 | 不得仅凭平均误差宣称工程可用 | [场景需求书 s05] |

### 校准数值

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认 MAX_RELATIVE_L2 | 0.1 | [场景需求书] | 默认阈值 |
| 默认 RUN_OOD_TEST | true | [场景需求书] | 建议开启 |
| 默认指标 | distribution_distance, diversity, physics_residual, coverage | [场景需求书] | 可扩展 |

## 边界与分流

- PASS → 模型可用，报告适用域与复核建议
- REJECT → 模型不达标，回退到 s03 调整训练或 s02 调整切分
- BLOCKED → 关键输入缺失或物理约束无法评估，停止并报告阻塞原因
- OOD 测试失败 → 明确标注适用域边界，域外工况必须 CFD 复核

## 质量检查

- 统计与物理指标同时报告
- 最差样本可追溯
- 结论含适用域限制与复核建议

## 回退策略

- 验收 REJECT → 回到 s03 调整训练策略
- 物理指标不达标 → 回到 s04 调整物理筛选阈值
- 适用域过窄 → 考虑扩大训练数据覆盖范围

## 资源召回建议

- 需要了解验收标准时召回本卡
- 需要了解适用域判定方法时召回本卡
- 需要了解 OOD 检测方法时召回相关论文证据

## 证据来源

[1] Physics-Informed Diffusion Models, 2024
[2] Learning Distributions of Complex Fluid Simulations with Diffusion Graph Networks, Lino et al., ICLR 2025, arXiv:2504.02843
[3] Uni-Flow: a unified autoregressive-diffusion model for complex multiscale flows, Xue et al., 2026, arXiv:2602.15592
[4] 场景需求书 CFD_S091 s05
