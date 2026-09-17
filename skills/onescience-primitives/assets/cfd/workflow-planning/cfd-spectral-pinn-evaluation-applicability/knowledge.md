# 谱增强PINN任务验收与适用域判定

## 适用范围

**触发条件**：
- 谱增强PINN工作流的第五步：验收评估
- 已完成方程求解与残差恢复

**适用场景**：
- 评估谱增强PINN求解结果的统计误差与物理一致性
- 判定模型适用域与泛化能力
- 生成验收报告与PASS/REJECT/BLOCKED结论

**不适用场景**：
- 仅需快速误差估算
- 无物理约束的纯数据驱动模型评估

## 输入

- solution_fields/、pde_residuals/（来自s04）
- METRICS：验收指标列表
- MAX_RELATIVE_L2：相对误差门限
- RUN_OOD_TEST：是否外推测试

## 输出

- evaluation.json：逐变量误差、边界误差、守恒/方程残差、最差样本、推理成本
- worst_cases.csv：最差样本详情
- applicability_report.md：适用域报告
- PASS_REJECT_BLOCKED.txt：验收结论

## 流程节点

### Step 1：统计误差评估
- **操作**：计算相对L2误差、相对L1误差、最大误差
- **参数**：{METRICS}
- **质量门禁**：统计指标逐变量报告

### Step 2：物理约束评估
- **操作**：计算PDE残差、边界误差、守恒误差
- **质量门禁**：物理指标逐项报告；最差样本可追溯

### Step 3：外推测试（可选）
- **操作**：几何或工况外推测试，评估泛化能力
- **参数**：{RUN_OOD_TEST}
- **质量门禁**：外推误差不急剧恶化；适用域边界明确

### Step 4：计算收益评估
- **操作**：记录推理时间、内存占用、与CFD方法对比
- **质量门禁**：计算成本可比较

### Step 5：验收结论
- **操作**：综合评估，输出PASS/REJECT/BLOCKED
- **参数**：{MAX_RELATIVE_L2}
- **质量门禁**：结论含适用域限制与复核建议

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 相对L2误差门限 | 0.1 | 场景需求书 | 测试集放行阈值 |
| 验收指标 | relative_L2, PDE_residual, boundary_error, conservation_error | 场景需求书 | 统计+物理指标 |
| 外推测试 | true | 场景需求书 | 默认启用 |

## 边界与分流

- **统计指标达标但物理指标超标**：REJECT（物理一致性不足）
- **物理指标达标但统计指标超标**：分析最差样本，考虑是否可接受
- **外推测试失败**：明确适用域边界，建议CFD复核

## 质量检查

- 统计与物理指标同时报告
- 最差样本可追溯
- 结论含适用域限制与复核建议

## 回退策略

- 验收不通过 → 分析失败原因，调整模型或配点策略后重训
- OOD测试失败 → 降低适用域声明，增加工况覆盖训练

## 资源召回建议

- 当需要执行谱增强PINN验收评估时召回本卡
- 配套资源：cfd-spectral-pinn-equation-solving-residual-recovery（上游）

## 证据来源

[1] "Neuro-Spectral Architectures for Causal Physics-Informed Networks", Bizzi et al., NeurIPS 2025, DOI: 10.48550/arXiv.2509.04966
