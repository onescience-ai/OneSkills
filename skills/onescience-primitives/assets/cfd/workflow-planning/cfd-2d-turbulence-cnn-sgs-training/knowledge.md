# 二维湍流CNN SGS模型训练

## 适用范围
本卡片描述二维湍流LES亚格子闭合任务的CNN模型训练步骤，负责配置网络架构、执行训练并保存最佳权重。适用于从预处理后的DNS数据训练CNN SGS模型。

## 输入
- **模型名称**：CNN SGS model（默认）
- **训练配置**：框架（PyTorch）、epochs、batch_size、learning_rate、seed、early_stopping_patience
- **切分数据**：来自预处理阶段的train/validation/test数据
- **归一化统计量**：用于数据变换的统计量
- **初始权重**：可选的预训练权重（用于迁移学习）

## 输出
- **best_checkpoint.pt**：验证损失最低的模型权重
- **train_config.json**：训练配置记录
- **training_metrics.csv**：逐轮训练验证指标
- **environment.txt**：代码版本、依赖、随机种子

## 流程节点

### 数据加载
1. **加载切分数据**：读取train/validation/test数据
2. **应用归一化**：使用训练集统计量进行数据变换
3. **构建数据加载器**：配置batch_size、shuffle等

### 模型配置
4. **选择网络架构**：全卷积神经网络（FCNN）或其他CNN变体
5. **定义损失函数**：MSE、MAE或其他物理约束损失
6. **配置优化器**：Adam、SGD等，设置学习率

### 训练执行
7. **训练循环**：逐epoch训练，记录loss
8. **验证评估**：每个epoch在验证集上评估
9. **早停策略**：验证损失不再下降时停止
10. **最佳权重保存**：保存验证损失最低的模型

### 记录保存
11. **配置记录**：保存所有超参数
12. **指标记录**：保存逐轮训练验证指标
13. **环境记录**：保存代码版本、依赖、随机种子

## 关键参数

### 通用判据
| 参数 | 判据 | 来源 | 说明 |
|------|------|------|------|
| 训练收敛 | 训练验证损失均为有限值 | [1] | 基本质量门禁 |
| 权重可复现 | 最佳权重可重新加载 | [1] | 可复现性要求 |
| 随机种子 | 配置环境随机种子可复现 | [1] | 可复现性要求 |
| 早停 | 验证损失不再下降时停止 | [1] | 防止过拟合 |

### 校准数值（来自特定体系）
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 典型epochs | 100 | [1] | 视数据集大小和收敛速度调整 |
| 典型batch_size | 8 | [1] | 视GPU显存调整 |
| 典型learning_rate | 0.001 | [1] | 可配合学习率调度器 |
| early_stopping_patience | 15 | [1] | 视收敛速度调整 |

## 边界与分流
- **训练不收敛**：调整学习率、batch_size、网络架构
- **过拟合**：增加数据增强、添加正则化、使用早停
- **欠拟合**：增加网络容量、训练轮数
- **初始权重不兼容**：检查网络架构是否匹配

## 质量检查
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

## 回退策略
- 训练失败：调整超参数、更换网络架构
- 过拟合：增加数据、添加正则化
- 欠拟合：增加网络容量

## 资源召回建议
- **场景启动**：当用户需要为二维湍流LES任务训练CNN SGS模型时召回
- **配套资源**：`cfd-2d-turbulence-data-ingestion`（数据接入）、`cfd-2d-turbulence-coupled-cfd-simulation`（后验耦合）

## 证据来源
[1] Guan Y, Chattopadhyay A, Subel A, et al. Stable a posteriori LES of 2D turbulence using convolutional neural networks: Backscattering analysis and generalization to higher Re via transfer learning. Journal of Computational Physics, 2022.
[2] Maulik R, San O, Rasheed A, Vedula P. Sub-grid modelling for two-dimensional turbulence using neural networks. Journal of Fluid Mechanics, 2018.
