# 连续坐标PDE任务验收与适用域判定

## 适用范围
本卡描述如何为潜空间与神经场连续PDE算子学习进行任务验收与适用域判定。适用于批量推理完成后、最终交付前的评估阶段。

## 输入
- METRICS：验收指标列表
- MAX_RELATIVE_L2：相对误差门限
- RUN_OOD_TEST：是否执行外推测试
- 推理结果与真实值

## 输出
- evaluation.json：评估指标
- worst_cases.csv：最差样本
- applicability_report.md：适用域报告
- PASS_REJECT_BLOCKED.txt：验收结论

## 流程节点
1. 按验收指标评价推理结果
2. 报告逐变量误差、边界误差、守恒或方程残差
3. 分析最差样本
4. 计算推理成本
5. 若执行外推测试，测试几何或工况外推能力
6. 给出PASS、REJECT或BLOCKED结论

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 验收指标 | relative_L2, RMSE, conservation_residual, boundary_error | 场景需求书 | 统计与物理指标 |
| 相对L2误差门限 | 0.1 | 场景需求书 | 测试集放行阈值 |
| 外推测试 | true | 场景需求书 | 默认执行OOD测试 |

## 边界与分流
- 仅凭平均误差宣称工程可用 → 禁止，必须分析最差样本与适用域
- 域外工况 → 必须经CFD复核，不得直接工程应用
- 统计与物理指标不一致 → 需深入分析原因，可能返回s02或s03

## 质量检查
- 统计与物理指标同时报告
- 最差样本可追溯
- 结论含适用域限制与复核建议

## 回退策略
验收不通过时，分析最差样本特征，检查是否为域外工况或数据质量问题，必要时返回s02调整切分策略或s03调整训练配置。

## 资源召回建议
当任务涉及PDE算子模型验收、需要评估适用域时召回本卡。

## 证据来源
[1] Latent Neural Operator for Solving Forward and Inverse PDE Problems
[2] Neural Emulator Superiority: When Machine Learning for PDEs Surpasses its Training Data
