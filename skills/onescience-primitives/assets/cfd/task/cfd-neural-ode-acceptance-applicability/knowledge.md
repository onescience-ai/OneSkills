# 任务验收与适用域判定（Neural ODE动力学学习）

## 适用范围

稳定性约束神经微分方程建模流程的第五步：评估统计误差、关键物理约束、泛化能力和计算收益。适用于判断模型是否满足工程可用标准，并明确适用域边界与复核建议。

## 输入

- {METRICS}: 验收指标列表（必填），默认relative_L2, RMSE, conservation_residual, boundary_error
- {MAX_RELATIVE_L2}: 相对误差门限（可选），默认0.1
- {RUN_OOD_TEST}: 是否外推测试（可选），默认true

## 输出

- evaluation.json: 评估结果（逐变量误差、边界误差、守恒残差）
- worst_cases.csv: 最差样本详情（可追溯）
- applicability_report.md: 适用域报告（含外推测试结果）
- PASS_REJECT_BLOCKED.txt: 验收判定

## 流程节点

```
按METRICS评价s04结果 → 报告逐变量误差/边界误差/守恒残差 → 分析最差样本和推理成本 → 使用MAX_RELATIVE_L2判定 → 执行外推测试（可选）→ 明确适用域限制与复核建议
```

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 验收指标 | relative_L2, RMSE, conservation_residual, boundary_error | [场景需求书s05] | 统计与物理指标必须同时报告 |
| 相对误差门限 | 0.1 | [场景需求书s05] | 测试集放行阈值 |
| 外推测试 | true | [场景需求书s05] | 几何或工况外推测试 |

## 边界与分流

- 相对L2误差超过门限 → REJECT，需调整模型或数据
- 物理约束违反严重 → REJECT，需增加物理正则化
- 域外工况测试失败 → 明确适用域限制，建议CFD复核
- 统计与物理指标不可兼得 → 两指标均需报告，不可省略

## 质量检查

- 统计与物理指标同时报告
- 最差样本可追溯（可定位到具体数据点）
- 结论含适用域限制与复核建议
- 不得仅凭平均误差宣称工程可用

## 回退策略

- 误差超标 → 分析误差来源（数据/模型/评估），针对性优化
- 物理违反 → 增加物理约束损失、调整网络结构
- 域外失败 → 缩小适用域范围，增加域外数据训练
- 评估指标不足 → 补充物理一致性指标

## 资源召回建议

- 本卡片为任务级卡片，对应工作流s05步骤
- 配套场景卡：cfd-stability-constrained-neural-ode-dynamics-learning
- 配套工作流卡：cfd-stability-constrained-neural-ode-workflow

## 证据来源

[1] CFD_S065场景需求书, scenario_catalogs/fluid/, 2026
