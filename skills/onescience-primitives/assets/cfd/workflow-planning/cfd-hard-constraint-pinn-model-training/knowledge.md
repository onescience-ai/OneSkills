# 模型配置与训练

## 适用范围

本卡片描述硬约束PINN复杂几何边界求解工作流的第三步：模型配置与训练。适用于：
- 训练Hard-constraint PINN、Boundary PINN
- 完成指定输入到目标物理量的映射
- 记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重

**不适用场景**：
- 完整流场数据的正问题求解
- 无物理约束的数据处理

## 输入

1. **模型名称** `{MODEL_NAME}`：实现或模型注册名
2. **训练配置** `{TRAIN_CONFIG}`：超参数和随机种子
3. **初始权重** `{INIT_CHECKPOINT}`：可选预训练权重

## 输出

1. **最佳模型权重** `best_checkpoint.pt`：通过训练门限权重
2. **训练配置** `train_config.json`：超参数配置
3. **训练指标** `training_metrics.csv`：逐轮训练验证指标
4. **环境信息** `environment.txt`：代码版本、依赖等

## 流程节点

```
加载s02切分与统计量 → 初始化模型 → 配置训练参数 → 记录代码版本依赖 → 记录随机种子 → 训练模型 → 记录逐轮指标 → 保存最佳权重
```

### 详细操作

#### 1. 数据加载

**操作**：
- 加载s02切分与统计量
- 验证数据格式正确
- 确保数据可被模型使用

**判定标准**：
- 数据加载成功
- 数据格式正确
- 统计量可用

#### 2. 模型初始化

**操作**：
- 初始化Hard-constraint PINN或Boundary PINN模型
- 检查模型架构正确
- 如提供初始权重，检查结构兼容性

**判定标准**：
- 模型初始化成功
- 模型架构正确
- 初始权重兼容（如提供）

#### 3. 训练配置

**操作**：
- 配置训练超参数
- 设置随机种子
- 配置优化器、损失函数等

**判定标准**：
- 超参数配置正确
- 随机种子设置完成
- 优化器、损失函数配置正确

#### 4. 训练执行

**操作**：
- 执行模型训练
- 记录逐轮训练验证指标
- 实现早停机制

**判定标准**：
- 训练过程稳定
- 损失函数收敛
- 早停机制正常工作

#### 5. 模型保存

**操作**：
- 保存最佳模型权重
- 保存训练配置
- 保存训练指标
- 保存环境信息

**判定标准**：
- 最佳权重可重新加载
- 训练配置完整
- 训练指标完整
- 环境信息完整

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 训练验证损失 | 有限值 | [场景需求书s03] | 训练验证损失均为有限值 |
| 最佳权重可加载 | 必须通过 | [场景需求书s03] | 最佳权重可重新加载 |
| 配置环境可复现 | 必须通过 | [场景需求书s03] | 配置环境随机种子可复现 |

### 校准数值

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 框架 | PyTorch | [场景需求书s03] | 默认训练框架 |
| 训练轮数 | 100 | [场景需求书s03] | 默认训练轮数，可根据收敛情况调整 |
| 批大小 | 8 | [场景需求书s03] | 默认批大小，可根据显存调整 |
| 学习率 | 0.001 | [场景需求书s03] | 默认学习率 |
| 随机种子 | 42 | [场景需求书s03] | 可复现性种子 |
| 早停耐心 | 15 | [场景需求书s03] | 早停轮数 |

以下数值来自CFD_S040场景，供量级校准；其他体系需以自身证据重新锚定。

## 边界与分流

1. **训练不收敛** → 调整网络架构、学习率或损失权重
2. **初始权重不兼容** → 检查模型架构，重新加载或重新训练
3. **内存不足** → 减小批大小或网络规模
4. **过拟合** → 增加正则化、调整网络复杂度

## 质量检查

1. **训练稳定性**：训练过程无异常波动
2. **损失收敛性**：损失函数收敛到可接受水平
3. **权重可加载性**：最佳权重可重新加载
4. **配置完整性**：训练配置、指标、环境信息完整
5. **可复现性**：相同随机种子下结果可复现

## 回退策略

1. **训练失败** → 检查数据格式、模型架构、超参数
2. **权重保存失败** → 检查存储空间、文件权限
3. **配置保存失败** → 手动记录配置信息
4. **环境信息缺失** → 手动记录环境信息

## 资源召回建议

**何时召回本卡片**：
- 需要执行硬约束PINN复杂几何边界求解的模型训练阶段
- 需要配置PINN训练参数
- 需要保存训练指标和模型权重

**配套资源**：
- 场景卡：cfd-hard-constraint-pinn-complex-geometry-solution
- 工作流卡：cfd-hard-constraint-pinn-complex-geometry-workflow
- 任务卡：cfd-hard-constraint-pinn-data-intake-contract-validation
- 任务卡：cfd-hard-constraint-pinn-preprocessing-data-splitting
- 任务卡：cfd-hard-constraint-pinn-equation-solving-residual-recovery
- 任务卡：cfd-hard-constraint-pinn-acceptance-applicability

## 证据来源

[1] Nonparametric Boundary Geometry in Physics Informed Deep Learning, 2020
[2] Solving Differential Equations with Constrained Learning, 2020
[3] Hybrid Boundary Physics-Informed Neural Networks for Solving Navier–Stokes Equations with Complex Boundary Conditions, 2025, URL: https://arxiv.org/abs/2507.17535
[4] SPINN: Separable Physics-Informed Neural Networks, 2021
[5] A Unified Hard-Constraint Framework for Solving Geometrically Complex PDEs, 2023
[6] Error analysis for physics informed neural networks (PINNs) approximating Kolmogorov PDEs, 2021, URL: https://arxiv.org/abs/2106.14473
[7] 场景需求书CFD_S040：硬约束PINN复杂几何边界求解，s03步骤定义