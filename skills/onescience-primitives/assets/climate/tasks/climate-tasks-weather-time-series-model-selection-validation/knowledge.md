# 气象时序预报模型选择与验证规范

## 适用范围
适用于earth域气象时序预报任务的模型选择与验证，覆盖短期（24-72小时）、中期（3-15天）预报。支持LSTM、Transformer、GRU等深度学习模型在气象预报中的应用。

## 输入
- 多站点历史温湿风数据
- 时空对齐后的标准输入数据
- 模型配置参数（序列长度、隐藏层维度、层数等）
- 训练/验证/测试数据划分

## 输出
- 方法工件与配置身份报告
- 输入输出兼容性矩阵
- 最小干运行日志
- 模型验证报告

## 流程节点
1. 方法工件身份验证 → 2. 输入输出兼容性检查 → 3. 最小干运行 → 4. 随机种子固定 → 5. 模型训练 → 6. 性能验证

每步含：操作、参数、工具、质量门禁

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 序列长度 | 24-168小时 | [论文1] | 根据预报时效选择，24h预报用24-48h序列 |
| 隐藏层维度 | 64-256 | [论文2] | 根据数据复杂度调整 |
| 层数 | 2-4 | [论文2] | 避免过深导致梯度消失 |
| 学习率 | 1e-4至1e-3 | [论文3] | 常用初始值，可根据收敛情况调整 |
| 批量大小 | 32-128 | [论文3] | 根据GPU内存调整 |

## 边界与分流
- 序列长度不匹配时：调整模型输入层或数据预处理
- 梯度爆炸/消失时：调整学习率或使用梯度裁剪
- 过拟合时：增加正则化、减少模型复杂度或增加数据
- 干运行失败时：检查数据格式、维度匹配和内存使用

## 质量检查
- 验证输入输出shape匹配
- 检查前向传播输出无NaN/Inf
- 验证梯度计算正常
- 确认随机种子固定

## 回退策略
- 模型选择不当：回退到更简单的模型（如线性回归、ARIMA）
- 干运行失败：修复数据或模型配置后重试
- 训练不收敛：调整超参数或更换优化器

## 资源召回建议
当执行气象预报模型选择与验证步骤时召回本卡片，配套资源包括模型配置模板、干运行检查工具和性能评估脚本。

## 证据来源
[1] Short-Term Weather Forecast Skill of Artificial Neural Networks, Christopher C. Hennon et al., Weather and Forecasting, 2022, DOI: 10.1175/waf-d-22-0009.1
[2] Redefining multi-target weather forecasting with a novel deep learning model: Hierarchical temporal convolutional long short-term memory with attention (HTC-LSTM-Attn) in Bangladesh, Md Anamul Kabir et al., PLOS One, 2026, DOI: 10.1371/journal.pone.0342431
[3] Enhancing Weather Forecasting Integrating LSTM and GA, Rita Teixeira et al., Applied Sciences, 2024, DOI: 10.3390/app14135769