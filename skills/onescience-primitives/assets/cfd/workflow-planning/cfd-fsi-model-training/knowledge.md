# 流固耦合逆向设计模型配置与训练

## 适用范围
流固耦合逆向设计的第三步，训练Differentiable physics、Graph simulator完成指定输入到目标物理量的映射，记录训练过程和最佳权重。适用于任何需要训练可微物理或图模拟器模型的流固耦合逆向设计任务。

## 输入
- 模型名称（{MODEL_NAME}）：实现或模型注册名
- 训练配置（{TRAIN_CONFIG}）：超参数和随机种子
- 初始权重（{INIT_CHECKPOINT}，可选）：可选预训练权重

## 输出
- 最佳模型权重（best_checkpoint.pt）
- 训练配置（train_config.json）
- 训练指标（training_metrics.csv）
- 环境信息（environment.txt）

## 流程节点
```
s03 模型配置与训练
  │  1. 使用{MODEL_NAME}，默认Differentiable physics、Graph simulator
  │  2. 使用{TRAIN_CONFIG}训练模型
  │  3. 加载s02切分与统计量
  │  4. 记录代码版本、依赖、随机种子
  │  5. 记录逐轮训练验证指标与最佳权重
  │  6. 若提供{INIT_CHECKPOINT}须检查结构兼容性
  │  7. 缺少必填输入时返回BLOCKED并列出缺项
  │  8. 不得编造数据、权重、工况或结果
  │  质量门禁：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现
```

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 训练框架 | PyTorch | 场景需求书s03 | 默认训练框架 |
| 早停耐心 | 15 | 场景需求书s03 | 防止过拟合 |
| 结构兼容性 | 检查 | 场景需求书s03 | 确保初始权重可用 |

### 校准数值
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 训练轮次 | 100 | 场景需求书s03 | 以下数值来自场景默认配置，其他体系需以自身证据重新锚定 |
| 批大小 | 8 | 场景需求书s03 | |
| 学习率 | 0.001 | 场景需求书s03 | |
| 随机种子 | 42 | 场景需求书 | |

## 边界与分流
- 缺少必填输入时返回BLOCKED并列出缺项
- 训练损失为NaN/Inf时REJECT并检查数据或模型配置
- 初始权重结构不兼容时返回BLOCKED并说明原因
- 训练不收敛时调整超参数或检查数据质量

## 质量检查
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现
- 训练指标完整记录

## 回退策略
- 训练不收敛时调整超参数
- 数据质量有问题时返回s02重新预处理
- 模型配置错误时检查模型定义

## 资源召回建议
- 本卡片为任务级卡片，可被以下需求召回：FSI模型训练、流固耦合模型配置、模型配置与训练
- 配套工作流卡片：cfd-differentiable-physics-fsi-inverse-design-workflow
- 配套场景卡片：cfd-differentiable-physics-fsi-inverse-design-scenario

## 证据来源
[1] PRDP_ Progressively Refined Differentiable Physics
[2] PETAL_ Physics Emulation Through Averaged Linearizations for Solving Inverse Problems