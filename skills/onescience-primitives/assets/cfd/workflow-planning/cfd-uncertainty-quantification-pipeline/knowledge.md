# 不确定性量化步骤的完整执行流程

## 适用范围
面向概率模型训练后的不确定性量化任务，生成预测分布、不确定性分解和校准分析。适用于需要量化预测不确定性的科学计算任务，如流场反演、参数识别等。

## 输入
- 训练好的模型权重
- 测试集数据
- 模型结构定义
- 不确定性量化参数（MC 采样次数、置信水平等）

## 输出
- predictive_distribution/：每个测试样本的预测分布（均值、方差）
- uncertainty_decomposition.json：偶然不确定性 vs 认知不确定性分解
- calibration.csv：各置信水平的覆盖率和平均区间宽度

## 流程节点
1. **模型加载**：加载训练好的模型权重
2. **MC 采样**：对测试集进行多次随机采样
3. **预测分布计算**：计算每个样本的预测均值和方差
4. **不确定性分解**：分解为偶然不确定性和认知不确定性
5. **置信区间计算**：计算均值±k*标准差的置信区间
6. **校准分析**：计算 reliability diagram 和 expected calibration error
7. **分布外检测**：使用 Mahalanobis 距离或能量分数
8. **结果输出**：生成三个标准产物

每步质量门禁：
- MC 采样次数足够（通常 ≥ 10）
- 预测方差合理（不为零或无穷大）
- 校准误差在可接受范围内

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| MC 采样次数 | 50 | [D1] | 影响不确定性估计精度 |
| 置信水平 | 0.95 | [D1] | 常用置信水平 |
| 分布外检测方法 | Mahalanobis 距离 | [D1] | 检测异常样本 |
| 校准指标 | Expected Calibration Error | [D2] | 衡量校准质量 |

## 边界与分流
- 如果 MC 采样次数不足：增加采样次数以提高估计精度
- 如果不确定性分解不合理：检查模型是否真正学习了不确定性
- 如果校准误差过大：使用温度缩放或 Platt 缩放进行校准

## 质量检查
- 验证点：预测分布方差 > 0
- 阈值：校准误差 < 0.1
- 失败处理：重新检查模型训练质量

## 回退策略
- 如果 MC 采样计算量过大：使用 MC Dropout 近似
- 如果校准失败：使用非参数校准方法

## 资源召回建议
- 何时召回：当模型训练完成后需要量化不确定性时
- 配套资源：不确定性量化脚本模板、校准分析工具

## 补充证据（开源文档/用户自有，可选）
[D1] Uncertainty Quantification in Machine Learning, arXiv, v1, URL: https://arxiv.org/abs/2011.09544（accessed_at 2026-09-17，交叉验证）
[D2] Calibration of Uncertainty Estimates, arXiv, v1, URL: https://arxiv.org/abs/1706.04599（accessed_at 2026-09-17，单源参考）

## 证据来源
[1] Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). On calibration of modern neural networks. In International Conference on Machine Learning (pp. 1321-1330).
[2] Kendall, A., & Gal, Y. (2017). What uncertainties do we need in Bayesian deep learning for computer vision? In Advances in Neural Information Processing Systems (pp. 5574-5584).