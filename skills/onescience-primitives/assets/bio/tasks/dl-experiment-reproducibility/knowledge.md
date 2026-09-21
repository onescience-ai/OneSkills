# 深度学习实验可复现性规范

## 适用范围
适用于深度学习实验可复现性保证的场景，需要同时固定numpy random seed、torch random seed（CPU和CUDA）、Python random seed、以及设置torch.backends.cudnn.deterministic。

## 输入
- 实验配置参数
- 随机种子值
- 可复现性配置

## 输出
- 固定随机种子的训练脚本
- 可复现性验证报告
- 实验环境记录

## 流程节点
1. 随机种子设置 → 2. 环境配置 → 3. 训练执行 → 4. 结果验证 → 5. 可复现性检查

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| numpy random seed | 42 | [1] | NumPy随机种子 |
| torch random seed | 11 | [1] | PyTorch随机种子 |
| Python random seed | 42 | [1] | Python随机种子 |
| cudnn.deterministic | True | [1] | 确定性算法 |

## 边界与分流
- GPU不可用时：仅设置CPU种子
- 种子设置失败时：使用默认种子并记录
- 可复现性验证失败时：重新设置种子并重试

## 质量检查
- 种子设置检查：确保所有随机源都固定
- 环境一致性检查：确保训练环境一致
- 结果一致性检查：确保多次运行结果一致
- 完整性检查：确保可复现性记录完整

## 回退策略
- 种子设置失败时：使用默认种子并记录
- 可复现性验证失败时：重新设置种子并重试
- 环境不一致时：使用容器化环境

## 资源召回建议
- 当任务需要保证实验可复现性时召回本卡片
- 配套资源：PyTorch官方文档、可复现性最佳实践

## 证据来源
[1] Leakage and the reproducibility crisis in machine-learning-based science, Patterns, 2023, DOI: 10.1016/j.patter.2023.100804
[2] PyTorch官方文档（https://pytorch.org/docs/stable/notes/randomness.html）