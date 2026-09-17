# PDE模型配置与训练任务

## 适用范围
适用于PDE基础模型零样本预测场景的模型训练阶段，训练PDE foundation model、In-context learner完成指定输入到目标物理量的映射。不适用于已有预训练模型或不需要训练的场景。

## 输入
- 模型名称（PDE foundation model、In-context learner）
- 训练配置（超参数、随机种子）
- 切分数据（来自预处理步骤）
- 初始权重（可选预训练权重）

## 输出
- best_checkpoint.pt（最佳模型权重）
- train_config.json（训练配置）
- training_metrics.csv（训练指标）
- environment.txt（环境信息）

## 流程节点
加载切分与统计量 → 记录代码版本、依赖、随机种子 → 逐轮训练验证 → 记录指标与最佳权重 → 检查初始权重兼容性

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 模型名称 | PDE foundation model、In-context learner | 场景需求书 | 实现或模型注册名 |
| 框架 | PyTorch | 场景需求书 | 训练框架 |
| 训练轮数 | 100 | 场景需求书 | 默认训练轮数 |
| 批大小 | 8 | 场景需求书 | 默认批大小 |
| 学习率 | 0.001 | 场景需求书 | 默认学习率 |
| 随机种子 | 42 | 场景需求书 | 可复现性保证 |
| 早停耐心 | 15 | 场景需求书 | 防止过拟合 |

## 边界与分流
- **训练验证损失非有限值**：检查数据质量、模型配置，必要时调整超参数。
- **最佳权重无法重新加载**：检查模型架构兼容性，确保保存时包含完整状态。
- **初始权重结构不兼容**：跳过初始权重，从随机初始化开始。

## 质量检查
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

## 回退策略
- 训练失败：调整超参数、更换模型架构、使用预训练权重。
- 过拟合：增加正则化、使用早停、增加数据量。
- 欠拟合：增加模型容量、调整学习率、增加训练轮数。

## 资源召回建议
当用户需要进行PDE基础模型零样本预测的模型训练时召回本卡片。配套资源包括：模型实现、训练脚本、配置工具。

## 补充证据（开源文档/用户自有，可选）
无

## 证据来源
[1] Zebra: In-Context Generative Pretraining for Solving Parametric PDEs, Louis Serrano et al., arXiv, 2024, DOI: 10.48550/arXiv.2410.03437
[2] Physics-informed Temporal Alignment for Auto-regressive PDE Foundation Models, 2024
[3] Zero-shot forecasting of chaotic systems, 2024
[4] Multiple Physics Pretraining for Spatiotemporal Surrogate Models, 2024
[5] MetaPhysiCa: Improving OOD Robustness in Physics-informed Machine Learning, 2024
[6] FLUID-LLM: Learning Computational Fluid Dynamics with Spatiotemporal-aware Large Language Models, Max Zhu et al., arXiv, 2024, DOI: 10.48550/arXiv.2406.04501