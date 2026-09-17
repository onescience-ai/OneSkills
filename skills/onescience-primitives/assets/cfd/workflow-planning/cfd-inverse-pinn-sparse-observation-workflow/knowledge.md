# 物理信息网络稀疏观测参数反演工作流

## 适用范围

本卡片描述使用物理信息神经网络（PINN）从稀疏流场观测中反演PDE参数的完整工作流。适用于：
- 稀疏传感器数据的流场参数推断
- 未知PDE系数的逆问题求解
- 物理约束与数据驱动融合的参数识别

**不适用场景**：
- 完整观测的正问题求解
- 无物理约束的纯数据回归
- 域外工况需经CFD复核

## 输入

1. **稀疏流场观测数据**：有限空间/时间点的流场变量
2. **PDE方程定义**：控制方程及待反演参数
3. **边界条件信息**：已知或部分已知的边界约束

## 输出

1. **反演参数估计**：推断的PDE参数值
2. **重建流场**：基于反演参数的完整预测
3. **物理残差场**：PDE方程在各配点的残差
4. **适用域报告**：模型可靠性的量化评估

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

### 详细步骤

#### Step 1: 数据接入与契约核验 (s01)

**操作**：接入稀疏流场观测与未知PDE参数，核验样本、变量、单位、网格坐标及许可。

**输入**：
- `{DATASET_PATH}`：数据集路径
- `{DATASET_NAME}`：数据集名称
- `{DATA_CONTRACT}`：数据契约（变量单位网格定义）

**输出**：
- `dataset_manifest.json`：数据清单
- `data_contract.json`：机器可读契约
- `data_audit.md`：审计报告

**质量门禁**：
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏

---

#### Step 2: 预处理与数据切分 (s02)

**操作**：统一物理量与表示，按几何、工况或时间构造无泄漏切分。

**输入**：
- `{SPLIT_CONFIG}`：切分配置（默认train:0.7, val:0.15, test:0.15）
- `{TARGET_FIELDS}`：目标变量列表
- `{NONDIMENSIONALIZE}`：是否无量纲化

**输出**：
- `train_manifest.json`：训练集清单
- `validation_manifest.json`：验证集清单
- `test_manifest.json`：测试集清单
- `normalization.json`：归一化统计量

**质量门禁**：
- 三份切分的对象轨迹互斥
- 仅用训练集计算变换统计量
- 边界与掩膜语义未破坏

---

#### Step 3: 模型配置与训练 (s03)

**操作**：训练Inverse PINN、Physics-informed data assimilation完成指定输入到目标物理量的映射。

**输入**：
- `{MODEL_NAME}`：模型名称
- `{TRAIN_CONFIG}`：训练配置（epochs, batch_size, learning_rate, seed等）
- `{INIT_CHECKPOINT}`：初始权重（可选）

**输出**：
- `best_checkpoint.pt`：最佳权重
- `train_config.json`：训练配置
- `training_metrics.csv`：训练指标
- `environment.txt`：环境信息

**质量门禁**：
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

---

#### Step 4: 方程求解与物理残差恢复 (s04)

**操作**：在查询配点或网格上恢复解场、导数、边界值与方程残差。

**输入**：
- `{CHECKPOINT}`：模型权重
- `{DEVICE}`：计算设备
- `{BATCH_SIZE}`：推理批大小

**输出**：
- `solution_fields/`：解场文件
- `pde_residuals/`：PDE残差
- `boundary_residuals.csv`：边界残差

**质量门禁**：
- 解场导数与残差均为有限值
- 边初值逐项满足门限
- 独立数值解或解析解可对照

---

#### Step 5: 任务验收与适用域判定 (s05)

**操作**：评估统计误差、关键物理约束、泛化能力和计算收益。

**输入**：
- `{METRICS}`：验收指标（relative_L2, PDE_residual, boundary_error, conservation_error）
- `{MAX_RELATIVE_L2}`：相对误差门限
- `{RUN_OOD_TEST}`：是否外推测试

**输出**：
- `evaluation.json`：评估结果
- `worst_cases.csv`：最差样本
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
| 切分比例 | train:0.7, val:0.15, test:0.15 | [场景需求书] | 标准数据切分 |
| 早停耐心 | 15 epochs | [场景需求书] | 防止过拟合 |
| 相对误差门限 | 0.1 | [场景需求书] | 测试集放行阈值 |
| 无量纲化 | true | [场景需求书] | 统一跨工况量纲 |

### 校准数值（以下数值来自CFD_S038场景，供量级校准；其他体系需以自身证据重新锚定）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| epochs | 100 | [场景需求书] | 训练轮数 |
| batch_size | 8 | [场景需求书] | 批量大小 |
| learning_rate | 0.001 | [场景需求书] | 学习率 |

## 边界与分流

1. **数据接入失败**：文件不可读或样本不足 → 返回BLOCKED，列出缺项
2. **切分泄漏**：同一轨迹帧被打散 → 重新按几何/工况切分
3. **训练不收敛**：损失为NaN或Inf → 调整学习率或损失权重
4. **物理残差过大**：PDE残差超过门限 → 检查方程定义或配点分布
5. **域外工况**：测试工况超出训练分布 → 执行CFD复核

## 质量检查

1. **数据阶段**：样本可追溯、变量完整、无泄漏
2. **预处理阶段**：切分互斥、统计量正确、语义保持
3. **训练阶段**：损失有限、权重可加载、可复现
4. **求解阶段**：残差有限、边界满足、可对照
5. **验收阶段**：多指标报告、最差可追溯、适用域明确

## 回退策略

1. **数据不足** → 引入先验知识或降阶模型
2. **训练失败** → 传统优化方法（遗传算法、粒子群）
3. **物理约束过强** → 自适应权重调整
4. **计算资源不足** → 子问题分解

## 资源召回建议

**何时召回本卡片**：
- 需要执行完整的PINN参数反演工作流
- 需要5步骤流程的详细操作指南
- 需要质量检查点和验收标准

**配套资源**：
- 场景卡：cfd-inverse-pinn-sparse-observation-parameter-inversion
- 任务卡：cfd-inverse-pinn-data-ingestion-contract-validation
- 任务卡：cfd-inverse-pinn-preprocessing-data-split
- 任务卡：cfd-inverse-pinn-model-training
- 任务卡：cfd-inverse-pinn-equation-solving-residual-recovery
- 任务卡：cfd-inverse-pinn-evaluation-applicability

## 证据来源

[1] Inferring flow parameters and turbulent configuration with physics-informed data assimilation and spectral nudging, 2018, URL: https://arxiv.org/abs/1804.07680
[2] Physics informed deep learning (Part I): Data-driven solutions of nonlinear partial differential equations, 2017, URL: https://arxiv.org/abs/1711.10561
[3] Physics-informed learning of governing equations from scarce data, 2020, URL: https://arxiv.org/abs/2005.03448
