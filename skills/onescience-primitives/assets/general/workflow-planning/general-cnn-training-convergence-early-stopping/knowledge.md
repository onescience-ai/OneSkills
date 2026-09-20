# 卷积神经网络训练收敛与早停策略

## 适用范围
面向卷积神经网络（CNN）训练任务，提供收敛判断标准、早停策略选择、训练/验证损失曲线分析方法，以及训练配置记录要求。适用于湍流闭合模型、图像分割、场预测等CNN训练场景，不适用于循环神经网络或Transformer训练。

## 输入
- 训练数据集：输入-输出对（如滤波速度场-亚格子应力）
- 验证数据集：独立数据集用于监控泛化能力
- 训练配置：学习率、优化器、损失函数、batch size、最大epoch数

## 输出
- 训练好的模型权重（best_checkpoint.pt）
- 训练配置文件（train_config.json）
- 训练指标记录（training_metrics.csv）
- 环境信息（environment.txt）

## 流程节点
1. 配置准备 → 2. 训练执行 → 3. 收敛监控 → 4. 早停判断 → 5. 产物生成

### 步骤1：配置准备
- 操作：定义训练超参数和记录要求
- 参数：学习率、优化器、损失函数、batch size、early_stopping_patience
- 工具：配置管理
- 质量门禁：配置完整，包含所有必要参数

### 步骤2：训练执行
- 操作：执行训练循环，记录每个epoch的训练/验证损失
- 参数：batch size=50，验证比例20%
- 工具：PyTorch训练循环
- 质量门禁：每个epoch记录训练损失和验证损失到training_metrics.csv

### 步骤3：收敛监控
- 操作：分析训练/验证损失曲线
- 参数：patience=15（连续15个epoch无改善则停止）
- 工具：损失曲线可视化
- 质量门禁：验证损失连续patience个epoch无改善时触发早停

### 步骤4：早停判断
- 操作：判断是否触发早停
- 参数：验证损失改善阈值（如1e-4）
- 工具：早停逻辑
- 质量门禁：记录早停epoch和最终验证损失

### 步骤5：产物生成
- 操作：保存模型权重和训练配置
- 参数：保存最佳验证损失对应的模型权重
- 工具：模型保存、配置序列化
- 质量门禁：输出目录包含四个标准产物

## 关键参数
### 通用判据
| 参数 | 判据 | 来源 | 说明 |
|------|------|------|------|
| 训练epoch数 | 50-200（根据收敛情况） | [1][2] | CNN SGS模型通常需要50-200个epoch才能收敛 |
| early_stopping_patience | 15-30 | [1][2] | 连续patience个epoch无改善则停止 |
| 验证比例 | 20% | [1] | 用于监控泛化能力 |
| batch size | 32-100 | [1][2] | 根据GPU内存调整 |
| 学习率 | 1e-3-1e-4 | [1][2] | 配合ADAM优化器 |

### 校准数值
以下数值来自湍流闭合模型训练研究，供量级校准；其他任务需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 最大epoch数 | 200 | [1] | 确保充分收敛 |
| 训练时间 | ~20分钟/200 epochs（单GPU） | [1] | NVIDIA Volta 100 |
| batch size | 50 | [1] | 40训练+10验证 |
| 损失函数 | MSE（单cell值） | [1] | 用于场预测任务 |

## 边界与分流
- **前提1：训练数据质量足够** → 不成立时：先检查DNS数据质量，再调整训练策略
- **前提2：验证损失持续下降** → 不成立时：检查学习率是否过大，数据是否过拟合
- **前提3：训练配置完整** → 不成立时：补充train_config.json、training_metrics.csv、environment.txt

## 质量检查
- 检查outputs/s03_training/包含四个标准产物
- 验证training_metrics.csv记录每个epoch的训练/验证损失
- 确认早停epoch和最终验证损失

## 回退策略
- 若训练仅7个epoch停止，检查数据质量和学习率
- 若验证损失不下降，尝试降低学习率或增加数据增强

## 资源召回建议
- 执行CNN训练前召回本卡片
- 训练收敛判断时召回本卡片
- 训练产物完整性检查时召回本卡片

## 证据来源
[1] Arumapperuma et al., "Extrapolation Performance of CNN-Based Combustion Models for LES", Flow Turbulence and Combustion, 2025, DOI: 10.1007/s10494-025-00643-w
[2] Guan et al., "Learning physics-constrained subgrid-scale closures in the small-data regime", Physica D Nonlinear Phenomena, 2022, DOI: 10.1016/j.physd.2022.133568