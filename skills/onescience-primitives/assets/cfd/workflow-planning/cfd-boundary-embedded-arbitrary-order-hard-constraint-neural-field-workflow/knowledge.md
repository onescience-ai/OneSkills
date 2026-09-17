# 边界嵌入与任意阶硬约束神经场求解工作流

## 适用范围

本卡片描述边界嵌入与任意阶硬约束神经场求解的完整工作流，适用于：
- 复杂几何边界的Navier-Stokes方程求解
- 非结构化网格或无网格点云上的PDE神经算子学习
- 需要在推理阶段精确满足任意阶边界条件的物理一致性预测
- 跨几何形状的流场泛化预测（外推需CFD复核）

**不适用场景**：
- 规则网格上的简单PDE问题
- 仅关注统计误差、不要求精确边界满足的纯数据驱动回归
- 边界条件随时间剧烈变化的瞬态问题

## 输入

1. **几何边界描述**：复杂几何形状的参数化表示或点云数据
2. **边界条件**：Dirichlet、Neumann、Robin或混合边界条件的数学描述
3. **PDE方程**：待求解的偏微分方程（如Navier-Stokes方程）
4. **初始条件**：问题的初始状态（对瞬态问题）
5. **数据集路径**：包含训练数据的目录或清单文件

## 输出

1. **解场**：PDE的近似解（速度场、压力场等）
2. **物理残差**：方程残差、边界残差
3. **模型检查点**：训练后的神经网络权重
4. **评估报告**：误差分析、适用域判定
5. **适用域报告**：模型适用范围与复核建议

## 流程节点

```
数据接入与契约核验 (s01) → 预处理与数据切分 (s02) → 模型配置与训练 (s03) → 批量推理与物理恢复 (s04) → 任务验收与适用域判定 (s05)
```

### 步骤1: 数据接入与契约核验 (s01)

**操作**：
- 接入混合边界与复杂域PDE数据
- 核验样本、变量、单位、网格坐标及许可
- 建立数据清单和数据契约

**输入**：
- 数据集路径 `{DATASET_PATH}`
- 数据集名称 `{DATASET_NAME}`
- 数据契约 `{DATA_CONTRACT}`

**输出**：
- `dataset_manifest.json`：数据清单
- `data_contract.json`：机器可读契约
- `data_audit.md`：数据审计报告

**质量门禁**：
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏

### 步骤2: 预处理与数据切分 (s02)

**操作**：
- 统一物理量与表示
- 按几何、工况或时间构造无泄漏切分
- 保存统计量与可逆变换

**输入**：
- 切分配置 `{SPLIT_CONFIG}`
- 目标变量 `{TARGET_FIELDS}`
- 是否无量纲化 `{NONDIMENSIONALIZE}`

**输出**：
- `train_manifest.json`：训练集清单
- `validation_manifest.json`：验证集清单
- `test_manifest.json`：测试集清单
- `normalization.json`：归一化参数

**质量门禁**：
- 三份切分的对象轨迹互斥
- 仅用训练集计算变换统计量
- 边界与掩膜语义未破坏

### 步骤3: 模型配置与训练 (s03)

**操作**：
- 训练Boundary-embedded neural operator、Hard-constraint neural field
- 完成指定输入到目标物理量的映射
- 记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重

**输入**：
- 模型名称 `{MODEL_NAME}`
- 训练配置 `{TRAIN_CONFIG}`
- 初始权重 `{INIT_CHECKPOINT}`

**输出**：
- `best_checkpoint.pt`：最佳模型权重
- `train_config.json`：训练配置
- `training_metrics.csv`：训练指标
- `environment.txt`：环境信息

**质量门禁**：
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

### 步骤4: 批量推理与物理恢复 (s04)

**操作**：
- 加载训练好的模型
- 在测试参数、边界和查询坐标上求解目标PDE
- 反归一化恢复物理单位、坐标网格、边界掩膜及任务派生量
- 保存逐样本结果和耗时

**输入**：
- 模型权重 `{CHECKPOINT}`
- 计算设备 `{DEVICE}`
- 推理批大小 `{BATCH_SIZE}`

**输出**：
- `predictions/`：预测结果
- `inference_manifest.json`：推理清单
- `timing.csv`：耗时统计

**质量门禁**：
- 预测无NaN或Inf且形状单位正确
- 每个测试样本有唯一结果
- 推理未使用测试目标校正

### 步骤5: 任务验收与适用域判定 (s05)

**操作**：
- 评估统计误差、关键物理约束、泛化能力和计算收益
- 使用验收指标给出PASS、REJECT或BLOCKED
- 执行几何或工况外推测试并明确适用域

**输入**：
- 验收指标 `{METRICS}`
- 相对误差门限 `{MAX_RELATIVE_L2}`
- 是否外推测试 `{RUN_OOD_TEST}`

**输出**：
- `evaluation.json`：评估结果
- `worst_cases.csv`：最差案例
- `applicability_report.md`：适用域报告
- `PASS_REJECT_BLOCKED.txt`：验收结论

**质量门禁**：
- 统计与物理指标同时报告
- 最差样本可追溯
- 结论含适用域限制与复核建议

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 硬约束满足 | 必须精确满足 | [场景需求书s03] | 边界条件必须精确满足，非软约束近似 |
| 任意阶微分 | 支持任意阶 | [场景需求书] | 支持任意阶微分约束的硬约束满足 |
| 无网格配点 | 适用于复杂几何 | [场景需求书s01] | 不依赖结构化网格，适用于任意几何形状 |
| 物理残差 | 有限值 | [场景需求书s04] | PDE方程残差必须为有限值 |
| 边界误差 | 有限值 | [场景需求书s05] | 边界条件满足程度必须可量化 |
| 相对L2误差 | 默认<0.1 | [场景需求书s05] | 测试集放行阈值 |

### 校准数值

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 训练轮数 | 100 | [场景需求书s03] | 默认训练轮数，可根据收敛情况调整 |
| 批大小 | 8 | [场景需求书s03] | 默认批大小，可根据显存调整 |
| 学习率 | 0.001 | [场景需求书s03] | 默认学习率 |
| 早停耐心 | 15 | [场景需求书s03] | 早停轮数 |
| 随机种子 | 42 | [场景需求书s03] | 可复现性种子 |
| 训练集比例 | 0.7 | [场景需求书s02] | 默认训练集比例 |
| 验证集比例 | 0.15 | [场景需求书s02] | 默认验证集比例 |
| 测试集比例 | 0.15 | [场景需求书s02] | 默认测试集比例 |

以下数值来自CFD_S064场景，供量级校准；其他体系需以自身证据重新锚定。

## 边界与分流

1. **数据不可读或缺失** → 返回BLOCKED，列出缺项
2. **切分导致数据泄漏** → 重新切分，确保对象轨迹互斥
3. **训练不收敛** → 调整网络架构、学习率或损失权重
4. **边界条件难以硬约束** → 考虑使用软约束方法作为对比
5. **PDE残差过大** → 增加配点数量或调整损失函数权重
6. **域外工况误差大** → 需要CFD复核，明确适用域限制

## 质量检查

1. **数据完整性**：所有必需字段均有定义
2. **切分正确性**：训练、验证、测试集互斥
3. **训练收敛性**：损失函数收敛到可接受水平
4. **解场正确性**：解满足PDE方程和边界条件
5. **评估全面性**：统计与物理指标同时报告
6. **可复现性**：相同随机种子下结果可复现

## 回退策略

1. **PINN不收敛** → 尝试调整网络架构（增加层数/神经元数）
2. **边界条件难以硬约束** → 考虑使用软约束方法作为对比
3. **计算资源不足** → 减小网络规模或使用降阶模型
4. **复杂几何难以参数化** → 使用点云表示或自适应网格
5. **评估指标不达标** → 根据最差案例分析原因，调整模型或数据

## 资源召回建议

**何时召回本卡片**：
- 需要执行边界嵌入与任意阶硬约束神经场求解的完整流程
- 需要了解边界嵌入神经算子求解PDE的工作流步骤
- 需要边界嵌入模型的训练和评估流程
- 需要复杂几何边界PDE问题的解决方案

**配套资源**：
- 场景卡：cfd-boundary-embedded-arbitrary-order-hard-constraint-neural-field-scenario
- 任务卡：cfd-boundary-embedded-neural-operator-data-intake-contract-validation
- 任务卡：cfd-boundary-embedded-neural-operator-preprocessing-data-splitting
- 任务卡：cfd-boundary-embedded-neural-operator-model-training
- 任务卡：cfd-boundary-embedded-neural-operator-batch-inference-physical-recovery
- 任务卡：cfd-boundary-embedded-neural-operator-acceptance-applicability

## 证据来源

[1] BENO: Boundary-Embedded Neural Operators for PDEs, 2024
[2] Harnessing the Power of Neural Operators with Automatically Encoded Conservation Laws, 2024
[3] Scaling Physics-Informed Hard Constraints with Mixture-of-Experts, 2024
[4] Neural Fields with Hard Constraints of Arbitrary Differential Order, 2024
[5] Physics-Embedded Neural Networks: Graph Neural PDE Solvers with Mixed Boundary Conditions, 2024
[6] 场景需求书CFD_S064：边界嵌入与任意阶硬约束神经场求解，workflow步骤定义
