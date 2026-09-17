# 任务验收与适用域判定

## 适用范围

**触发条件**：
- 已完成方程求解与物理残差恢复（s04）
- 需要对求解结果进行最终验收和适用域判定

**适用场景**：
- Deep Ritz网络求解结果的验收
- 弱形式神经求解器结果的验收
- 需要明确工程可用性和适用域的场景

**不适用场景**：
- 仅需快速评估（可用简化指标）
- 求解结果尚未完成（s04未执行）

## 输入

- **METRICS**（必需）：验收指标列表
- **MAX_RELATIVE_L2**（可选）：相对误差门限，默认0.1
- **RUN_OOD_TEST**（可选）：是否外推测试，默认true
- s04产出的solution_fields、pde_residuals、boundary_residuals

## 输出

- **evaluation.json**：评估结果汇总
- **worst_cases.csv**：最差样本列表
- **applicability_report.md**：适用域报告
- **PASS_REJECT_BLOCKED.txt**：判定结果

## 流程节点

### 1. 统计误差评估
- 计算逐变量相对L2误差
- 计算全局统计指标（均值、方差、最大值）
- 识别最差样本

### 2. 物理约束评估
- 评估PDE残差（方程满足程度）
- 评估边界残差（边界条件满足程度）
- 评估守恒误差（如有守恒律）

### 3. 泛化能力评估
- 在测试集上评估
- 执行几何或工况外推测试（OOD）
- 评估不同区域的误差分布

### 4. 推理成本评估
- 记录推理时间
- 评估计算资源消耗
- 与传统方法对比（如有baseline）

### 5. 综合判定
- 基于所有指标给出PASS/REJECT/BLOCKED
- 生成适用域报告
- 标记需要CFD复核的域外工况

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| relative_L2 | ≤ 0.1 | [1] | 默认放行阈值 |
| PDE_residual | 有限值 | [2] | 方程满足程度 |
| boundary_error | ≤ 门限 | [2] | 边界满足程度 |
| conservation_error | 有限值 | [1] | 守恒律满足程度 |
| OOD测试 | true | [1] | 默认启用外推测试 |

## 边界与分流

- **指标全部通过**：判定为PASS，输出适用域报告
- **部分指标不通过**：判定为REJECT，列出失败原因
- **关键指标缺失**：判定为BLOCKED，要求补充数据
- **域外工况**：必须标记为"需CFD复核"

## 质量检查

- [ ] 统计与物理指标同时报告
- [ ] 最差样本可追溯
- [ ] 结论含适用域限制与复核建议
- [ ] 判定结果明确（PASS/REJECT/BLOCKED）

## 回退策略

- 评估指标不足 → 补充计算并重新评估
- 判定不确定 → 倾向于REJECT或BLOCKED
- 域外工况 → 必须经CFD复核

## 资源召回建议

本卡是Deep Ritz工作流的最后一步。判定结果决定是否工程可用：
- PASS → 可用于目标工况
- REJECT → 需要改进模型或数据
- BLOCKED → 需要补充信息
- 域外工况 → 必须经CFD复核

## 证据来源

[1] "Learning from Integral Losses in Physics-Informed Neural Networks", 2024
[2] "Efficient Error Certification for Physics-Informed Neural Networks", 2024
[3] "Characterizing possible failure modes in physics-informed neural networks", 2021
