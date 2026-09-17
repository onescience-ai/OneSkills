# 对称PDE任务验收与适用域判定

## 适用范围

本卡片服务于等变PDE预测任务的最终验收阶段。在批量推理完成后，需要综合评估统计误差、物理约束满足度、泛化能力和计算收益，给出工程可用性判定。适用于任何PDE预测模型的验收评估。不适用于：仅需快速原型验证的场景（可简化评估）；模型尚在开发迭代中（应在训练阶段评估）。

## 输入

- s04输出的predictions/、inference_manifest.json
- 验收指标列表（{METRICS}）：默认relative_L2, RMSE, conservation_residual, boundary_error
- 相对误差门限（{MAX_RELATIVE_L2}）：默认0.1
- 是否外推测试（{RUN_OOD_TEST}）：默认true

## 输出

- evaluation.json：完整评估结果
- worst_cases.csv：最差样本详情
- applicability_report.md：适用域报告
- PASS_REJECT_BLOCKED.txt：最终验收判定

## 流程节点

1. **逐变量误差计算** → relative L2、RMSE等统计指标
2. **边界误差评估** → 边界条件满足度
3. **守恒或方程残差** → 物理守恒律检验
4. **最差样本识别** → 追溯最差样本来源
5. **推理成本评估** → 推理时间、内存占用
6. **OOD外推测试** → 几何或工况外推（若{RUN_OOD_TEST}为true）
7. **适用域报告生成** → 明确适用范围和复核建议
8. **验收判定** → PASS/REJECT/BLOCKED

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 统计与物理指标同时报告 | 强制 | 场景JSON s05 quality_gate | 不得仅报告统计指标 |
| 最差样本可追溯 | 强制 | 场景JSON s05 quality_gate | 可追溯到具体样本 |
| 适用域限制与复核建议 | 强制 | 场景JSON s05 quality_gate | 结论必须包含 |
| OOD测试 | 默认开启 | 场景JSON s05 | 域外工况必须经CFD复核 |
| 验收判定三态 | PASS/REJECT/BLOCKED | 场景JSON s05 prompt | 明确判定 |

### 校准数值（来自CFD_S063场景）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认指标 | relative_L2, RMSE, conservation_residual, boundary_error | 场景JSON s05 default | |
| 相对误差门限 | 0.1 | 场景JSON s05 default | |

## 边界与分流

- **仅平均误差达标但最差样本超标**：REJECT，需改善鲁棒性
- **统计指标达标但物理约束违反**：REJECT，需引入物理正则化
- **OOD测试全部失败**：限定适用域为训练分布内，BLOCKED for OOD
- **计算成本过高**：在applicability_report中标注，建议模型压缩

## 质量检查

- 统计与物理指标同时报告（质量门禁）
- 最差样本可追溯（质量门禁）
- 结论含适用域限制与复核建议（质量门禁）
- PASS_REJECT_BLOCKED.txt为明确三态判定

## 回退策略

- 评估指标不足：补充物理约束评估后重新验收
- OOD测试设计不合理：调整外推范围重新测试

## 资源召回建议

当用户任务涉及以下场景时召回：
- "PDE验收"、"适用域判定"、"物理一致性评估"、"OOD测试"、"等变网络评估"
- 配套卡片：cfd-equivariant-pde-physical-consistency（物理一致性评估细节）、cfd-equivariant-pde-batch-inference（前一步推理）

## 证据来源

场景CFD_S063 workflow step s05定义。
[6] Self-Supervised Learning with Lie Symmetries for Partial Differential Equations
