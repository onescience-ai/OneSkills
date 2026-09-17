# 边界嵌入神经算子模型配置与训练

## 适用范围

本卡片描述边界嵌入神经算子模型配置与训练任务，适用于：
- Boundary-embedded neural operator的训练
- Hard-constraint neural field的训练
- 复杂几何边界PDE问题的神经算子学习

**不适用场景**：
- 标准神经算子（如FNO）的训练
- 软约束PINN的训练
- 简单几何边界问题

## 输入

1. **模型名称** `{MODEL_NAME}`：实现或模型注册名
2. **训练配置** `{TRAIN_CONFIG}`：超参数和随机种子
3. **初始权重** `{INIT_CHECKPOINT}`：可选预训练权重

## 输出

1. `best_checkpoint.pt`：最佳模型权重
2. `train_config.json`：训练配置
3. `training_metrics.csv`：训练指标
4. `environment.txt`：环境信息

## 流程节点

### Step 1：模型架构配置
- **操作**：配置Boundary-embedded neural operator、Hard-constraint neural field架构
- **工具**：PyTorch、神经算子库
- **质量门禁**：模型架构正确配置

### Step 2：数据加载
- **操作**：加载s02切分与统计量
- **工具**：数据加载工具
- **质量门禁**：数据加载正确，统计量可用

### Step 3：训练执行
- **操作**：执行模型训练，记录训练过程
- **工具**：PyTorch训练循环
- **质量门禁**：训练验证损失均为有限值

### Step 4：权重保存
- **操作**：保存最佳模型权重和训练配置
- **工具**：模型保存工具
- **质量门禁**：最佳权重可重新加载

### Step 5：环境记录
- **操作**：记录代码版本、依赖、随机种子
- **工具**：环境记录工具
- **质量门禁**：配置环境随机种子可复现

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 模型架构 | Boundary-embedded neural operator, Hard-constraint neural field | [场景需求书s03] | 必须使用指定模型架构 |
| 训练收敛 | 必须 | [场景需求书s03] | 训练验证损失均为有限值 |
| 权重可加载 | 必须 | [场景需求书s03] | 最佳权重必须可重新加载 |
| 可复现性 | 必须 | [场景需求书s03] | 配置环境随机种子可复现 |

### 校准数值

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| epochs | 100 | 场景需求书 | 默认训练轮数 |
| batch_size | 8 | 场景需求书 | 默认批量大小 |
| learning_rate | 0.001 | 场景需求书 | 默认学习率 |
| early_stopping_patience | 15 | 场景需求书 | 早停耐心值 |
| random_seed | 42 | 场景需求书 | 可复现性种子 |
| framework | PyTorch | 场景需求书 | 默认框架 |

以下数值来自CFD_S064场景，供量级校准；其他体系需以自身证据重新锚定。

## 边界与分流

1. **训练不收敛** → 调整网络架构、学习率或损失权重
2. **权重不可加载** → 检查模型架构兼容性
3. **不可复现** → 检查随机种子设置
4. **计算资源不足** → 减小网络规模或使用混合精度训练

## 质量检查

1. **架构正确性**：模型架构正确配置
2. **数据加载**：数据加载正确，统计量可用
3. **训练收敛**：训练验证损失均为有限值
4. **权重可加载**：最佳权重可重新加载
5. **可复现性**：相同随机种子下结果可复现

## 回退策略

1. **训练不收敛** → 调整超参数或网络架构
2. **资源不足** → 降低批量大小或使用混合精度训练
3. **架构不兼容** → 检查初始权重与模型架构

## 资源召回建议

**何时召回本卡片**：
- 需要训练Boundary-embedded neural operator
- 需要训练Hard-constraint neural field
- 需要复杂几何边界PDE问题的神经算子训练

**配套资源**：
- 工作流卡：cfd-boundary-embedded-arbitrary-order-hard-constraint-neural-field-workflow
- 任务卡：cfd-boundary-embedded-neural-operator-preprocessing-data-splitting
- 任务卡：cfd-boundary-embedded-neural-operator-batch-inference-physical-recovery

## 证据来源

[1] BENO: Boundary-Embedded Neural Operators for PDEs, 2024
[2] Neural Fields with Hard Constraints of Arbitrary Differential Order, 2024
[3] Scaling Physics-Informed Hard Constraints with Mixture-of-Experts, 2024
[4] 场景需求书CFD_S064：边界嵌入与任意阶硬约束神经场求解，workflow步骤定义
