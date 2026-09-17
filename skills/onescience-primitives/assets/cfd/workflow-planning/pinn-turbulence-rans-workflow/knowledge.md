# PINN湍流RANS均值流求解与闭合工作流

## 适用范围

本工作流用于PINN湍流RANS均值流求解与闭合的完整执行过程，涵盖从数据接入到验收评估的五个阶段。适用于需要从稀疏湍流数据重建完整物理场、验证物理一致性并评估模型适用域的CFD任务。

**触发条件**：
- 具备RANS方程描述和稀疏均值流湍流数据
- 需要物理一致的湍流场重建
- 需要评估模型在域外工况的适用性

## 输入

- **RANS方程**：Reynolds平均Navier-Stokes方程描述
- **稀疏均值流湍流数据**：来自实验或数值模拟的稀疏测量数据
- **数据集路径**：目录或清单文件
- **数据契约**：变量定义、单位、坐标系、网格拓扑

## 输出

- **可复现模型**：训练好的PINN模型权重与配置
- **完整湍流场**：解场、导数、通量、方程残差
- **评估报告**：统计误差、物理约束、适用域判定
- **验收结论**：PASS/REJECT/BLOCKED判定

## 流程节点

```
s01: 数据接入与契约核验
     ↓
s02: 预处理与数据切分
     ↓
s03: 模型配置与训练
     ↓
s04: 方程求解与物理残差恢复
     ↓
s05: 任务验收与适用域判定
```

### 步骤详细说明

#### s01: 数据接入与契约核验
- **操作**：接入RANS方程与稀疏均值流湍流数据，核验样本、变量、单位、网格坐标及许可
- **输入**：{DATASET_PATH}, {DATASET_NAME}, {DATA_CONTRACT}
- **输出**：dataset_manifest.json, data_contract.json, data_audit.md
- **质量门禁**：数据文件可读且样本可追溯、输入目标变量单位坐标定义完整、不存在训练测试泄漏

#### s02: 预处理与数据切分
- **操作**：统一物理量与表示，按几何、工况或时间构造无泄漏切分
- **输入**：{SPLIT_CONFIG}, {TARGET_FIELDS}, {NONDIMENSIONALIZE}
- **输出**：train_manifest.json, validation_manifest.json, test_manifest.json, normalization.json
- **质量门禁**：三份切分的对象轨迹互斥、仅用训练集计算变换统计量、边界与掩膜语义未破坏

#### s03: 模型配置与训练
- **操作**：训练Turbulence-augmented PINN完成指定输入到目标物理量的映射
- **输入**：{MODEL_NAME}, {TRAIN_CONFIG}, {INIT_CHECKPOINT}
- **输出**：best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt
- **质量门禁**：训练验证损失均为有限值、最佳权重可重新加载、配置环境随机种子可复现

#### s04: 方程求解与物理残差恢复
- **操作**：在查询配点或网格上恢复解场、导数、边界值与方程残差
- **输入**：{CHECKPOINT}, {DEVICE}, {BATCH_SIZE}
- **输出**：solution_fields/, pde_residuals/, boundary_residuals.csv
- **质量门禁**：解场导数与残差均为有限值、边初值逐项满足门限、独立数值解或解析解可对照

#### s05: 任务验收与适用域判定
- **操作**：评估统计误差、关键物理约束、泛化能力和计算收益
- **输入**：{METRICS}, {MAX_RELATIVE_L2}, {RUN_OOD_TEST}
- **输出**：evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt
- **质量门禁**：统计与物理指标同时报告、最差样本可追溯、结论含适用域限制与复核建议

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 相对L2误差门限 | 0.1 | 场景需求书 | 测试集放行阈值 |
| 训练框架 | PyTorch | 场景需求书 | 默认训练框架 |
| 早停耐心 | 15轮 | 场景需求书 | 防止过拟合 |
| 切分比例 | 70/15/15 | 场景需求书 | 训练/验证/测试比例 |

### 校准数值

以下数值来自CFD_S037场景，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认批大小 | 8 | 场景需求书 | 训练/推理批大小 |
| 默认学习率 | 0.001 | 场景需求书 | 优化器学习率 |
| 默认训练轮数 | 100 | 场景需求书 | 训练迭代次数 |
| 切分随机种子 | 42 | 场景需求书 | 可复现切分 |

## 边界与分流

**关键前提与改道**：

1. **前提：数据文件可读且样本可追溯**
   - 不成立时 → 返回BLOCKED并列出缺项，不得编造数据

2. **前提：训练验证损失均为有限值**
   - 不成立时 → 调整学习率、批大小或网络架构

3. **前提：解场导数与残差均为有限值**
   - 不成立时 → 检查模型权重、调整推理批大小或设备

4. **前提：统计与物理指标同时报告**
   - 不成立时 → 补充缺失指标后重新评估

## 质量检查

- **数据质量**：样本可追溯、变量完整、无泄漏
- **训练质量**：损失有限、权重可复现、随机种子固定
- **求解质量**：导数有限、边界满足、可对照验证
- **验收质量**：指标全面、最差可溯、适用域明确

## 回退策略

1. **数据不足**：转向数据增强或半监督学习
2. **训练不收敛**：调整超参数或网络架构
3. **物理残差过大**：增加物理损失权重或调整配点
4. **泛化不足**：增加工况多样性或迁移学习

## 资源召回建议

- 需要具体步骤实现时 → 召回对应task卡片（cfd-pinn-rans-*）
- 需要场景概述时 → 召回场景卡片（pinn-turbulence-rans-mean-flow-solving）
- 需要PINN训练方法时 → 召回cfd-pinn-rans-model-training
- 需要验收评估方法时 → 召回cfd-pinn-rans-acceptance-evaluation

## 证据来源

[1] Generalizable turbulence closures across bluff-body shapes by PINN-based solver-agnostic training, arXiv:2607.04491, 2026
[2] Physics-informed neural networks for solving Reynolds-averaged Navier–Stokes equations, arXiv:2107.10711, 2021
[3] Physics-informed data based neural networks for two-dimensional turbulence, arXiv:2203.02555, 2022
