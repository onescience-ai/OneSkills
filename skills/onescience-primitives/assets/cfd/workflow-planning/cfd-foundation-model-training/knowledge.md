# Model Configuration and Training

## 适用范围

面向预训练科学基础模型在目标任务上的迁移训练阶段，支持 PDE foundation model 和 Pretrained neural operator 的 fine-tuning 与 transfer learning。适用于需要利用预训练知识加速新物理场模型训练的场景。

## 输入

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| MODEL_NAME | str | 是 | 模型注册名或实现路径 |
| TRAIN_CONFIG | object | 是 | 训练配置：框架、超参数、种子 |
| INIT_CHECKPOINT | doc | 否 | 预训练权重路径 |

## 输出

| 产物 | 格式 | 说明 |
|------|------|------|
| best_checkpoint.pt | PyTorch | 最佳验证性能权重 |
| train_config.json | JSON | 完整训练配置 |
| training_metrics.csv | CSV | 逐轮训练验证指标 |
| environment.txt | Text | 代码版本、依赖、随机种子 |

## 流程节点

1. **加载切分数据** → 读取 s02 输出的 train/val manifest
2. **加载归一化参数** → 读取 normalization.json
3. **实例化模型** → 按 MODEL_NAME 创建模型实例
4. **加载预训练权重** → 若提供 INIT_CHECKPOINT，检查结构兼容性并加载
5. **配置优化器** → 按 TRAIN_CONFIG 设置优化器、学习率调度
6. **训练循环** → 逐 epoch 训练，记录 train/val loss
7. **早停检查** → 按 early_stopping_patience 判断是否停止
8. **保存最佳权重** → 按验证性能保存 best_checkpoint.pt
9. **记录环境** → 保存代码版本、依赖、随机种子

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 预训练权重检查 | 结构兼容性验证 | 场景需求书 | 防止架构不匹配 |
| 损失值 | 必须为有限值 | 场景需求书 | NaN/Inf 表示训练失败 |
| 最佳权重 | 必须可重新加载 | 场景需求书 | 确保 checkpoint 完整 |
| 随机种子 | 必须可复现 | 场景需求书 | 固定 seed=42 |

### 校准数值
> 以下数值来自场景需求书，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 框架 | PyTorch | 场景需求书 | 默认框架 |
| epochs | 100 | 场景需求书 | 最大轮次 |
| batch_size | 8 | 场景需求书 | 批大小 |
| learning_rate | 0.001 | 场景需求书 | 微调学习率 |
| seed | 42 | 场景需求书 | 随机种子 |
| early_stopping_patience | 15 | 场景需求书 | 早停耐心 |

## 边界与分流

- **预训练权重不可用**：从头训练（需更多数据与计算）
- **权重结构不兼容**：检查模型架构或修改加载逻辑
- **训练不收敛**：降低学习率、增加预热、检查数据质量
- **验证 loss 上升**：触发早停，保存当前最佳

## 质量检查

- [ ] 训练验证损失均为有限值
- [ ] 最佳权重可重新加载
- [ ] 配置环境随机种子可复现
- [ ] 训练指标已完整记录

## 回退策略

- 收敛失败 → 调整超参后重试
- 显存不足 → 减小 batch_size 或使用 gradient accumulation
- 权重加载失败 → 检查 checkpoint 格式与模型结构

## 资源召回建议

当需要执行预训练模型迁移训练时召回本卡片。

## 证据来源

[1] 场景需求书 CFD_S056 workflow s03 定义
