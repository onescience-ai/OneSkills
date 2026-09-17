# 模型配置与训练任务

## 适用范围
本任务适用于训练CNN、Aerodynamic foundation model完成翼型壁面压力剪切及速度测量数据到目标物理量的映射。适用于任何需要基于壁面测量数据进行气动力反演的场景。

## 输入
- 模型名称：实现或模型注册名。
- 训练配置：超参数和随机种子。
- 初始权重：可选预训练权重。

## 输出
- best_checkpoint.pt：最佳权重。
- train_config.json：训练配置。
- training_metrics.csv：训练指标。
- environment.txt：环境信息。

## 流程节点
1. 使用模型名称和训练配置训练模型。
2. 加载预处理切分与统计量。
3. 记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。
4. 若提供初始权重须检查结构兼容性。

## 关键参数
### 通用判据（方法层）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 训练验证损失均为有限值 | true | 质量门禁 | 避免数值问题 |
| 最佳权重可重新加载 | true | 质量门禁 | 模型可复现 |
| 配置环境随机种子可复现 | true | 质量门禁 | 实验可复现 |

### 校准数值（体系专属值）
以下数值来自翼型壁面压力剪切与积分气动力联合反演场景，供量级校准；其他体系需以自身证据重新锚定。
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 模型架构 | CNN、Aerodynamic foundation model | 场景需求书 | 默认模型 |
| 框架 | PyTorch | 场景需求书 | 训练框架 |
| 批大小 | 8 | 场景需求书 | 默认批大小 |
| 学习率 | 0.001 | 场景需求书 | 默认学习率 |
| 早停耐心 | 15 | 场景需求书 | 防止过拟合 |
| 训练轮数 | 100 | 场景需求书 | 默认训练轮数 |

## 边界与分流
- 当训练验证损失出现NaN或Inf时，需降低学习率或调整模型架构。
- 当最佳权重无法重新加载时，需检查模型结构兼容性。
- 当配置环境随机种子不可复现时，需检查随机种子设置。

## 质量检查
- 训练验证损失均为有限值。
- 最佳权重可重新加载。
- 配置环境随机种子可复现。

## 回退策略
- 若训练失败，可尝试降低学习率、调整批大小或使用学习率调度器。
- 若模型过拟合，可尝试增加早停耐心、使用正则化或数据增强。
- 若模型欠拟合，可尝试增加模型容量或训练轮数。

## 资源召回建议
当需要训练CNN或Aerodynamic foundation model进行气动力反演时召回本卡片。可配合以下卡片使用：
- cfd-data-preprocessing-task：预处理与数据切分。
- cfd-inference-task：批量推理与物理恢复。

## 证据来源
[1] Predicting the wall-shear stress and wall pressure through convolutional neural networks, Arivazhagan G. Balasubramanian, Luca Guastoni, Philipp Schlatter, Hossein Azizpour, Ricardo Vinuesa, 2023, DOI: 10.48550/arXiv.2303.00706
[2] Towards a Foundation-Model Paradigm for Aerodynamic Prediction in Three-dimensional Design, Yunjia Yang, Babak Gholami, Caglar Gurbuz, Mohammad Rashed, Nils Thuerey, 2026, DOI: 10.48550/arXiv.2604.18062