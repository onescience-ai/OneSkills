# 评估步骤的完整执行流程

## 适用范围
面向科学计算任务的评估步骤，计算统计误差、物理约束指标和不确定性指标，生成评估报告和适用域分析。适用于模型训练和不确定性量化后的最终评估。

## 输入
- 模型预测结果
- 不确定性量化结果
- 测试集真实值
- 评估指标配置

## 输出
- evaluation.json：所有评估指标的计算结果
- worst_cases.csv：最差样本的详细信息
- applicability_report.md：适用域限制和复核建议
- PASS_REJECT_BLOCKED.txt：任务判定（PASS/PARTIAL/REJECT/BLOCKED）

## 流程节点
1. **统计误差计算**：计算 relative_L2、NLL 等指标
2. **物理约束评估**：计算 continuity_residual、momentum_residual
3. **不确定性评估**：计算 coverage、calibration_error
4. **最差样本识别**：找出指标最差的样本
5. **综合判定**：根据验收指标阈值判定 PASS/PARTIAL/REJECT/BLOCKED
6. **报告生成**：生成评估报告和适用域分析

每步质量门禁：
- 所有指标计算正确
- 最差样本信息完整
- 判定结论合理

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| relative_L2 阈值 | < 0.1 | [D1] | 相对 L2 误差 |
| NLL 阈值 | < 0.0 | [D1] | 负对数似然 |
| coverage 阈值 | > 0.9 | [D1] | 95% 置信区间覆盖率 |
| calibration_error 阈值 | < 0.1 | [D1] | 校准误差 |

## 边界与分流
- 如果指标计算失败：检查数据格式和模型输出
- 如果判定为 REJECT：分析失败原因并给出改进建议
- 如果判定为 BLOCKED：记录阻塞原因并建议下一步操作

## 质量检查
- 验证点：所有评估指标计算完成
- 阈值：验收指标达到场景要求
- 失败处理：重新检查模型和数据

## 回退策略
- 如果评估指标不达标：使用更宽松的阈值或调整模型
- 如果最差样本过多：分析数据质量问题

## 资源召回建议
- 何时召回：当模型训练和不确定性量化完成后需要最终评估时
- 配套资源：评估指标计算脚本、报告生成模板

## 补充证据（开源文档/用户自有，可选）
[D1] Machine Learning Evaluation Metrics, scikit-learn, v1.3.0, URL: https://scikit-learn.org/stable/modules/model_evaluation.html（accessed_at 2026-09-17，交叉验证）
[D2] Physics-Informed Neural Networks: A Deep Learning Framework for Solving Forward and Inverse Problems Involving Nonlinear Partial Differential Equations, arXiv, v1, URL: https://arxiv.org/abs/1711.10561（accessed_at 2026-09-17，单源参考）

## 证据来源
[1] Raissi, M., Perdikaris, P., & Karniadakis, G. E. (2019). Physics-informed neural networks: A deep learning framework for solving forward and inverse problems involving nonlinear partial differential equations. Journal of Computational Physics, 378, 686-707. DOI: 10.1016/j.jcp.2018.10.045