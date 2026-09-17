# 算子评估与适用域判定

## 适用范围

**触发条件**：
- 已完成推理，需要评估模型性能与适用性
- 需要评估统计误差、物理约束、泛化能力
- 需要判定适用域与复核建议

**适用场景**：
- 算子学习工作流的验收阶段
- 需要确保模型满足工程应用要求
- 需要明确适用域限制与复核建议

**不适用场景**：
- 推理未完成或结果不可用
- 仅需快速验证的简单任务

## 输入

**必填输入**：
- {METRICS}：验收指标（统计和物理指标）

**可选输入**：
- {MAX_RELATIVE_L2}：相对误差门限（默认0.1）
- {RUN_OOD_TEST}：是否外推测试（默认true）

## 输出

**产物清单**：
- evaluation.json：评估结果
- worst_cases.csv：最差样本记录
- applicability_report.md：适用域报告
- PASS_REJECT_BLOCKED.txt：验收判定

## 流程节点

### 操作步骤
1. 按{METRICS}评价s04结果
2. 报告逐变量误差、边界误差、守恒或方程残差、最差样本和推理成本
3. 使用{MAX_RELATIVE_L2}及任务物理门限给出PASS、REJECT或BLOCKED
4. 若{RUN_OOD_TEST}为true，执行几何或工况外推测试并明确适用域
5. 不得仅凭平均误差宣称工程可用

### 关键指标
- 相对L2误差（relative_L2）
- 均方根误差（RMSE）
- 守恒残差（conservation_residual）
- 边界误差（boundary_error）

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认相对L2门限 | 0.1 | [场景S055] | 测试集放行阈值 |
| 默认验收指标 | relative_L2, RMSE, conservation_residual, boundary_error | [场景S055] | 统计与物理指标 |
| 外推测试 | true | [场景S055] | 测试域外工况 |

## 边界与分流

**异常处理**：
1. 误差超标 → 标记REJECT，分析原因并建议改进
2. 物理约束不满足 → 标记REJECT，建议增加物理正则化
3. 适用域过窄 → 明确标注限制，建议CFD复核
4. 最差样本不可接受 → 标记BLOCKED，要求重新评估

## 质量检查

**验证点**：
- 统计与物理指标同时报告
- 最差样本可追溯
- 结论含适用域限制与复核建议

**失败处理**：
- 任一验证点不通过 → 补充报告内容，确保完整性

## 回退策略

**替代方案**：
- 评估指标不足 → 补充更多物理约束指标
- 适用域判定困难 → 降级为保守估计并标注不确定性

## 资源召回建议

**何时召回**：
- 算子学习工作流的验收阶段
- 需要评估模型性能与适用性时
- 需要明确适用域限制时

**配套资源**：
- cfd-operator-inference-physical-recovery（推理恢复任务）
- cfd-multiscale-pde-operator-learning（场景级卡片）

## 证据来源

[1] Multiwavelet-based Operator Learning for Differential Equations, arXiv:2109.13459, 2021
[2] Spectral-Embedded Operator Learning for Three-Phase Interfacial Flow, arXiv:2608.29069, 2026
