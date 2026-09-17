# 自回归CFD模型训练

## 适用范围
自回归卷积神经网络（Autoregressive CNN）和 PDE-Refiner 等神经网络PDE求解器的训练任务。模型输入前K个时间步的流场快照，自回归输出后续时间步的流场预测。适用于圆柱绕流等非定常流场的长时滚动预测。

## 输入
- 模型名称（{MODEL_NAME}）：Autoregressive CNN 或 PDE-Refiner
- 训练配置（{TRAIN_CONFIG}）：框架、epochs、batch_size、learning_rate、seed、early_stopping_patience
- 初始权重（{INIT_CHECKPOINT}，可选）：预训练权重
- 训练集/验证集清单（来自s02）
- 归一化统计量（normalization.json）

## 输出
- 最佳模型权重（best_checkpoint.pt）
- 训练配置（train_config.json）
- 训练指标（training_metrics.csv）
- 环境信息（environment.txt）

## 流程节点
```
s03 模型配置与训练
  操作：
    1. 加载s02切分数据与归一化统计量
    2. 初始化模型（Autoregressive CNN 或 PDE-Refiner）
    3. 若提供{INIT_CHECKPOINT}则检查结构兼容性后加载
    4. 按{TRAIN_CONFIG}执行训练循环
    5. 记录代码版本、依赖、随机种子、逐轮训练验证指标
    6. 保存最佳权重

  参数：{MODEL_NAME}, {TRAIN_CONFIG}, {INIT_CHECKPOINT}
  质量门禁：
    - 训练验证损失均为有限值
    - 最佳权重可重新加载
    - 配置环境随机种子可复现
```

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 模型类型 | Autoregressive CNN / PDE-Refiner | 场景需求书 | 自回归网络，输入前K步预测后续步 |
| 最佳权重保存条件 | 验证集指标最优时保存 | 场景需求书s03 | 需可重新加载验证 |
| 环境记录 | 代码版本、依赖、随机种子 | 场景需求书s03 | 确保可复现 |

### 校准数值
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 框架 | PyTorch | 场景需求书s03 | 以下数值来自场景默认配置，其他体系需以自身证据重新锚定 |
| epochs | 100 | 场景需求书s03 | |
| batch_size | 8 | 场景需求书s03 | |
| learning_rate | 0.001 | 场景需求书s03 | |
| seed | 42 | 场景需求书s03 | |
| early_stopping_patience | 15 | 场景需求书s03 | |

## 边界与分流
- 缺少必填输入时返回BLOCKED并列出缺项，不得编造权重或结果
- 提供{INIT_CHECKPOINT}时须检查结构兼容性，不兼容则拒绝加载
- 训练损失为NaN/Inf时REJECT并检查数据质量或模型配置
- 验证集指标不收敛时调整超参数或检查数据切分

## 质量检查
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现
- 代码版本和依赖已记录

## 回退策略
- 训练不收敛时降低学习率或减小batch size
- 过拟合时增加正则化或调整early_stopping_patience
- 显存不足时减小batch_size或使用混合精度

## 资源召回建议
- 本卡片为任务级卡片，覆盖工作流步骤s03
- 配套工作流卡片：cfd-cylinder-wake-prediction-workflow
- 上游任务卡片：cfd-cylinder-wake-data-ingestion-preprocessing
- 下游任务卡片：cfd-cylinder-wake-inference-physics-recovery
