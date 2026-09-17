# Flow Matching 模型配置与训练

## 适用范围

本任务使用 Flow matching model 训练复杂流动概率代理模型。适用于流匹配概率代理构建流程的第三阶段。核心产出为可复现的 checkpoint、训练指标和环境记录。支持从零训练或基于预训练权重微调。

## 输入

- 模型名称（{MODEL_NAME}，默认 Flow matching model）
- 训练配置（{TRAIN_CONFIG}，含框架、 epochs、batch_size、learning_rate、seed、early_stopping_patience）
- 可选初始权重（{INIT_CHECKPOINT}）
- 预处理切分清单与归一化统计量（来自阶段 2）

## 输出

- best_checkpoint.pt（最佳模型权重）
- train_config.json（训练配置）
- training_metrics.csv（逐轮训练验证指标）
- environment.txt（代码版本、依赖、随机种子）

## 流程节点

1. 加载预处理切分与归一化统计量
2. 初始化 Flow matching model
3. 若提供初始权重，检查结构兼容性
4. 执行训练循环，记录逐轮指标
5. 早停判定（验证集无改善 patience 轮后停止）
6. 保存最佳 checkpoint 与环境记录
7. 输出训练配置与指标文件

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 框架 | PyTorch | [场景需求书] | 默认框架 |
| epochs | 100 | [场景需求书] | 默认训练轮数 |
| batch_size | 8 | [场景需求书] | 默认批次大小 |
| learning_rate | 0.001 | [场景需求书] | 默认学习率 |
| seed | 42 | [场景需求书] | 随机种子 |
| early_stopping_patience | 15 | [场景需求书] | 验证集无改善提前停止 |

## 边界与分流

- 初始权重结构不兼容：返回 BLOCKED，列出维度不匹配信息
- 训练损失发散：检查数据质量、学习率，必要时降低学习率或增大 batch_size
- 训练损失为 NaN/Inf：检查数据中的异常值，回退阶段 2 重新质控
- 验证损失不降：检查模型容量、数据分布，必要时调整网络结构

## 质量检查

- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现
- 逐轮指标完整记录

## 回退策略

- 训练不收敛 → 检查数据质量，回退阶段 2
- 框架版本不兼容 → 更新依赖或切换框架
- 内存不足 → 减小 batch_size 或使用梯度累积

## 资源召回建议

当用户需要训练 Flow matching model 进行 CFD 概率代理时召回本卡片。前置步骤：cfd-flow-matching-preprocessing-splitting。后续步骤：cfd-flow-matching-conditional-sampling-physics-filter。可参考 cfd-diffusion-stochastic-pde-probability-prediction-workflow 了解扩散模型训练的对比方法。

## 证据来源

[1] Switched Flow Matching: Eliminating Singularities via Switching ODEs, 2024
[2] Physics vs Distributions: Pareto Optimal Flow Matching with Physics Constraints, 2024
[3] Dflow-SUR: Enhancing Generative Aerodynamic Inverse Design using Differentiation Throughout Flow Matching, arXiv:2512.08336, 2025
[4] GeoFunFlow-3D: A Physics-Guided Generative Flow Matching Framework for High-Fidelity 3D Aerodynamic Inference over Complex Geometries, arXiv:2604.23350, 2026
[5] Physics-Guided Generative Surrogates for Parametric Rarefied Flows with Neural-Field Auto-Decoders: A Pipeline-Level Study of Flow Matching and Diffusion, arXiv:2608.25454, 2026
