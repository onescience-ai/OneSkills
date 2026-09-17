# 任务验收与适用域判定

## 适用范围

适用于湍流闭合模型训练与耦合完成后的最终验收评估。当需要判断模型是否满足工程应用要求、明确适用域边界时，执行本步骤。

## 输入

- METRICS：验收指标列表（closure_RMSE, mean_profile_error, spectrum_error, stability_horizon）
- MAX_RELATIVE_L2：相对误差门限（默认0.1）
- RUN_OOD_TEST：是否执行外推测试（默认true）

## 输出

- evaluation.json：完整评估结果
- worst_cases.csv：最差样本列表
- applicability_report.md：适用域报告
- PASS_REJECT_BLOCKED.txt：验收结论

## 流程节点

1. 加载s04结果 → 汇总先验/后验评估数据
2. 计算统计误差 → 逐变量RMSE、相对L2误差
3. 评估物理约束 → 能谱误差、守恒性、边界误差
4. 识别最差样本 → 追溯至原始数据
5. 计算推理成本 → 时间、内存、GPU占用
6. 外推测试（可选） → 几何或工况外推
7. 给出验收结论 → PASS/REJECT/BLOCKED
8. 生成适用域报告 → 明确限制与复核建议

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| MAX_RELATIVE_L2 | 0.1 | 场景需求书 | 默认误差门限 |
| RUN_OOD_TEST | true | 场景需求书 | 默认执行外推 |
| 验收指标 | closure_RMSE, mean_profile_error, spectrum_error, stability_horizon | 场景需求书 | 统计+物理 |

## 验收判据

### PASS条件
- 所有统计指标低于门限（MAX_RELATIVE_L2）
- 物理约束满足（能谱一致性、守恒性）
- 最差样本可追溯
- 推理成本可接受
- 适用域明确标注

### REJECT条件
- 任一关键指标超标
- 物理约束违反
- 后验求解发散

### BLOCKED条件
- 缺少必填输入
- 数据不可用
- 评估无法完成

## 边界与分流

- 平均误差达标但最差样本超标 → 仍可REJECT，建议针对最差工况优化
- 域内测试通过但外推失败 → PASS但标注适用域限制，建议CFD复核
- 推理成本过高 → 标注成本限制，建议模型压缩或蒸馏

## 质量检查

- 统计与物理指标同时报告
- 最差样本可追溯
- 结论含适用域限制与复核建议

## 回退策略

- 评估失败 → 降级为部分评估，标注缺失项
- 外推测试失败 → 明确标注不适用域
- 结论不确定 → BLOCKED，建议重新评估

## 资源召回建议

- 需要了解验收标准时召回本卡
- 需要了解适用域评估方法时召回本卡

## 证据来源

[1] Ilersich, A.F., Nair, P.B. (2025). Learning Stochastic Multiscale Models. arXiv:2506.22655.
[2] Grigo, C., Koutsourelakis, P.-S. (2019). Journal of Computational Physics, 397, 108842.
