# 连续坐标PDE模型配置与训练

## 适用范围
本卡描述如何为潜空间与神经场连续PDE算子学习配置和训练模型。适用于数据切分完成后、推理前的模型训练阶段。

## 输入
- MODEL_NAME：模型名称（Latent Neural Operator / Neural field operator）
- TRAIN_CONFIG：训练配置（框架、轮数、批大小、学习率、随机种子、早停耐心）
- 训练集与验证集清单
- 可选的初始权重检查点

## 输出
- best_checkpoint.pt：最佳模型权重
- train_config.json：训练配置记录
- training_metrics.csv：训练验证指标
- environment.txt：环境依赖记录

## 流程节点
1. 加载切分数据与统计量
2. 配置模型架构与优化器
3. 执行训练循环（含早停）
4. 记录代码版本、依赖、随机种子
5. 保存最佳权重

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 训练框架 | PyTorch | 场景需求书 | 默认深度学习框架 |
| 训练轮数 | 100 | 场景需求书 | 默认训练轮数 |
| 批大小 | 8 | 场景需求书 | 默认训练批大小 |
| 学习率 | 0.001 | 场景需求书 | 默认学习率 |
| 随机种子 | 42 | 场景需求书 | 可复现训练 |
| 早停耐心 | 15 | 场景需求书 | 防止过拟合 |

## 边界与分流
- 训练验证损失出现NaN/Inf → 检查数据预处理、学习率、模型架构
- 提供初始权重但结构不兼容 → 跳过加载，从头训练
- 缺少必填输入 → 返回BLOCKED，不得编造数据或权重

## 质量检查
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

## 回退策略
训练失败时，检查数据切分是否泄漏、预处理是否正确、模型架构是否适配数据维度。

## 资源召回建议
当任务涉及PDE算子模型训练、需要确保训练可复现时召回本卡。

## 证据来源
[1] Latent Neural Operator for Solving Forward and Inverse PDE Problems
[2] Operator Learning with Neural Fields: Tackling PDEs on General Geometries
