# 模型配置与训练（Stable Neural ODE）

## 适用范围

稳定性约束神经微分方程建模流程的第三步：配置Stable Neural ODE和Constrained Neural Process，完成指定输入到目标物理量的映射训练。适用于从预处理后的动力系统数据训练具有稳定性约束的连续时间动力学模型。

## 输入

- {MODEL_NAME}: 模型名称（必填），默认"Stable Neural ODE、Constrained neural process"
- {TRAIN_CONFIG}: 训练配置（必填），框架、超参数、随机种子
- {INIT_CHECKPOINT}: 初始权重（可选），预训练权重路径

## 输出

- best_checkpoint.pt: 最佳模型权重
- train_config.json: 训练配置
- training_metrics.csv: 逐轮训练验证指标
- environment.txt: 环境记录（代码版本、依赖、随机种子）

## 流程节点

```
加载模型架构 → 应用训练配置 → 加载s02切分与统计量 → 执行训练（记录逐轮指标）→ 保存最佳权重与配置
```

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 框架 | PyTorch | [场景需求书s03] | 默认实现 |
| Epochs | 100 | [场景需求书s03] | 可配置 |
| Batch size | 8 | [场景需求书s03] | 按显存调整 |
| 学习率 | 0.001 | [场景需求书s03] | 默认配置 |
| 随机种子 | 42 | [场景需求书s03] | 可复现性 |
| 早停耐心 | 15 | [场景需求书s03] | 防止过拟合 |

## 边界与分流

- 初始权重结构不兼容 → 检查模型架构差异，建议重新初始化
- 训练损失出现NaN/Inf → 检查学习率、数据归一化、数值稳定性
- 缺少必填输入 → 返回BLOCKED
- 显存不足 → 减小batch_size或使用梯度累积

## 质量检查

- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现
- 逐轮指标可追溯

## 回退策略

- 训练不收敛 → 降低学习率、增加正则化、检查数据质量
- 过拟合 → 增加数据增强、调整模型复杂度、启用早停
- 显存不足 → 减小batch_size、使用梯度累积

## 资源召回建议

- 本卡片为任务级卡片，对应工作流s03步骤
- 配套场景卡：cfd-stability-constrained-neural-ode-dynamics-learning
- 配套工作流卡：cfd-stability-constrained-neural-ode-workflow

## 证据来源

[1] Stabilized Neural Differential Equations for Learning Dynamics with Explicit Constraints, [场景需求书related_papers]
[2] CFD_S065场景需求书, scenario_catalogs/fluid/, 2026
