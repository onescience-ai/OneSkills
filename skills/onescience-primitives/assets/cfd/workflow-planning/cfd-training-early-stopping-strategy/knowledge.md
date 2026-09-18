# 训练轮数与早停策略关系

## 适用范围

面向深度学习模型训练任务，定义训练轮数（epochs）与早停策略（early stopping）的配置关系。适用于网格优化、物理场预测、科学计算等需要防止过拟合并确保模型充分收敛的场景。本卡规定了patience参数设置、收敛判断标准和最优checkpoint选择方法。

## 输入

- 模型训练配置（epochs、patience、min_delta等）
- 验证集数据
- 损失函数和优化器

## 输出

- 最优模型checkpoint
- 训练历史日志
- 收敛状态报告

## 流程节点

1. **配置初始化** → 设置epochs、patience、min_delta参数
2. **训练循环** → 执行epoch训练和验证
3. **损失监控** → 跟踪验证集损失变化
4. **早停判断** → 检查patience窗口内损失是否改善
5. **最优保存** → 保存验证损失最低的checkpoint
6. **训练终止** → 达到早停条件或最大epochs

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 最大epochs | >= 2 * patience | 领域规范 | 确保早停有足够空间触发 |
| patience参数 | 10-20轮 | 领域规范 | 等待改善的轮数 |
| min_delta | 1e-4 - 1e-3 | 领域规范 | 最小改善阈值 |
| 最优模型选择 | 验证损失最低 | [D1] | 避免过拟合 |
| checkpoint内容 | model+optimizer+epoch+loss | [D1] | 完整恢复信息 |

### 校准数值（体系专属）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认epochs | 100 | 工作流配置 | 标准训练长度 |
| 默认patience | 15 | 工作流配置 | 等待改善轮数 |
| 建议epochs下限 | 30 | 体系约束 | 至少2*patience |

## 边界与分流

- epochs < 2*patience：早停可能无法有效触发，模型可能欠拟合
- patience过大：训练时间延长，可能过拟合
- patience过小：可能在收敛前停止训练
- min_delta过小：对噪声敏感，可能提前停止
- min_delta过大：可能错过真正的改善

## 质量检查

- 验证epochs >= 2 * patience
- 检查训练日志中验证损失变化趋势
- 确认最优checkpoint对应最低验证损失
- 验证早停触发时的epoch记录
- 检查训练历史是否完整保存

## 回退策略

- 早停过早触发：增大patience重新训练
- 模型未收敛：增大全epochs或调整学习率
- 过拟合严重：增加正则化或减少模型复杂度
- 训练不稳定：调整min_delta或使用学习率调度

## 资源召回建议

- 当任务涉及模型训练、超参数调优、防止过拟合时召回本卡
- 配套资源：cfd-pytorch-model-save-load（模型保存）、cfd-adaptive-mesh-data-contract（数据格式）

## 补充证据

[D1] Saving and Loading Models, PyTorch Contributors, 2023, URL: https://pytorch.org/tutorials/beginner/saving_loading_models.html（accessed_at: 2026-09-17，权威文档）

## 证据来源

[1] PyTorch官方教程 - Saving and Loading Models, PyTorch Contributors, 2023, DOI: N/A