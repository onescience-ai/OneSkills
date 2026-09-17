# Symbolic PDE Model Training

## 适用范围
面向符号与稀疏PDE发现任务的模型配置与训练步骤。加载预处理后的切分数据，配置训练超参数，执行Symbolic physics learner或Sparse PDE discovery模型的训练，记录代码版本、依赖、随机种子和训练指标，确保可复现性。

## 输入
- **模型名称**（必填）：实现或模型注册名（默认Symbolic physics learner、Sparse PDE discovery）。
- **训练配置**（必填）：超参数和随机种子的结构化配置。
- **初始权重**（可选）：预训练权重路径，需检查结构兼容性。
- **切分数据**（来自s02）：train_manifest.json、validation_manifest.json及normalization.json。

## 输出
- **best_checkpoint.pt**：通过训练门限的最佳权重。
- **train_config.json**：完整训练配置记录。
- **training_metrics.csv**：逐轮训练验证指标。
- **environment.txt**：代码版本、依赖列表、随机种子。

## 流程节点
```
1. 加载s02切分数据与统计量
2. 加载{MODEL_NAME}模型架构
3. 应用{TRAIN_CONFIG}超参数
4. 若提供{INIT_CHECKPOINT}检查结构兼容性
5. 执行训练循环
6. 记录逐轮指标
7. 保存最佳权重
8. 输出环境信息
```

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 训练验证损失 | 均为有限值（非NaN/Inf） | [场景需求书] | 否则触发回退 |
| 最佳权重可重新加载 | 必须通过 | [场景需求书] | 权重文件完整性检查 |
| 随机种子可复现 | 必须可复现 | [场景需求书] | 记录在environment.txt |
| 初始权重兼容性 | 结构必须匹配 | [场景需求书] | 不匹配时拒绝加载 |

### 校准数值
> 以下数值来自场景需求书默认配置，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认框架 | PyTorch | [场景需求书] | — |
| 默认轮数 | 100 | [场景需求书] | 受早停控制 |
| 默认批大小 | 8 | [场景需求书] | 按显存调整 |
| 默认学习率 | 0.001 | [场景需求书] | — |
| 早停耐心 | 15轮 | [场景需求书] | — |
| 默认种子 | 42 | [场景需求书] | — |

## 边界与分流
- **缺少必填输入**：返回BLOCKED，列出缺项，不得编造数据或权重。
- **损失为非有限值**：检查梯度流和数据预处理，回退至s02。
- **初始权重不兼容**：拒绝加载，使用随机初始化重新训练。
- **早停触发**：保存早停时的最佳权重，记录实际训练轮数。

## 质量检查
1. 训练验证损失均为有限值。
2. 最佳权重文件可重新加载。
3. environment.txt包含完整依赖和种子信息。
4. training_metrics.csv包含逐轮记录。
5. train_config.json可被标准JSON解析。

## 回退策略
- 训练不收敛：调整学习率或增加早停耐心。
- 梯度爆炸：降低学习率或增加梯度裁剪。
- 内存不足：减小批大小。

## 资源召回建议
- 当需要为符号/稀疏方程发现训练模型时召回。
- 配套卡片：cfd-sparse-data-intake-and-contract-verification（数据接入）、cfd-pde-residual-recovery（残差恢复）。

## 证据来源
[1] 场景需求书 CFD_S045 s03定义
[2] Symbolic Physics Learner: Discovering governing equations via Monte Carlo tree search, 2022
[3] Universal Physics-Informed Neural Networks: Symbolic Differential Operator Discovery with Sparse Data, 2022
[4] Deep hidden physics models: Deep learning of nonlinear partial differential equations, 2018
