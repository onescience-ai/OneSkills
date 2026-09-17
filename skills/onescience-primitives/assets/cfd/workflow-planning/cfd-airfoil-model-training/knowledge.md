# 模型配置与训练任务

## 适用范围
本任务适用于训练核方法代理模型（Kernel surrogate）与生成模型（Diffusion model），完成从输入到目标物理量的映射。

## 输入
- 模型名称（Kernel surrogate、Diffusion model）
- 训练配置（超参数、随机种子）
- 切分后的训练、验证数据集
- 归一化统计量
- 可选初始权重

## 输出
- 最佳模型权重（best_checkpoint.pt）
- 训练配置（train_config.json）
- 训练指标（training_metrics.csv）
- 环境信息（environment.txt）

## 流程节点
1. 加载模型架构
2. 加载训练配置
3. 加载切分数据与统计量
4. 训练模型
5. 记录训练验证指标
6. 保存最佳权重
7. 记录环境信息

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 模型名称 | Kernel surrogate, Diffusion model | [场景需求书] | 默认模型 |
| 训练框架 | PyTorch | [场景需求书] | 默认框架 |
| 训练轮数 | 100 | [场景需求书] | 默认配置 |
| 批大小 | 8 | [场景需求书] | 默认配置 |
| 学习率 | 0.001 | [场景需求书] | 默认配置 |
| 随机种子 | 42 | [场景需求书] | 可复现性 |
| 早停耐心 | 15 | [场景需求书] | 默认配置 |

## 边界与分流
- 训练损失为NaN或Inf：检查数据或调整超参数。
- 验证损失不下降：调整学习率或模型架构。
- 权重不兼容：检查初始权重结构。
- 环境不一致：记录依赖版本。

## 质量检查
- 训练验证损失均为有限值。
- 最佳权重可重新加载。
- 配置环境随机种子可复现。

## 回退策略
- 训练失败：简化模型或增加数据。
- 验证不通过：调整超参数或检查数据。
- 权重不兼容：使用随机初始化重新训练。

## 资源召回建议
当用户需要训练核方法或生成模型时，可召回本任务卡片。配套资源包括：
- 模型架构实现
- 训练循环实现
- 超参数优化工具
- 环境记录工具

## 证据来源
[1] A Kernel-based Resource-efficient Neural Surrogate for Multi-fidelity Prediction of Aerodynamic Field, arXiv:2512.10287, 2025
[2] AFBench_ A Large-scale Benchmark for Airfoil Design, arXiv:1411.1784, 2014
[3] Airfoil optimization using Design-by-Morphing with minimized design-space dimensionality, arXiv:2510.16020, 2025
[4] Predictive Criteria for Electrospray-Assisted Droplet Dynamics in Aerodynamic Flow Fields, arXiv:2509.22676, 2025
[5] AeroJEPA_ Learning Semantic Latent Representations for Scalable 3D Aerodynamic Field Modeling, arXiv:2605.05586, 2026
[6] AirfoilGen_ A valid-by-construction and performance-aware latent diffusion model for airfoil generation, arXiv:2605.20303, 2026