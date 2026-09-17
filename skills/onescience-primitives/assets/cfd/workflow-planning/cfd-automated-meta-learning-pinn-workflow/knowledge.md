# 自动化与元学习PINN跨方程求解工作流

## 适用范围

面向PDE方程族的自动化PINN跨方程求解，提供从数据接入到适用域评估的完整五步工作流。适用于PDEBench、PINNacle等多方程基准，也可泛化到其他需要在统一框架内处理多种PDE类型的场景。

**触发条件**：用户需要训练一个PINN模型同时处理多个PDE方程，或需要自动化PDE求解流水线。

## 输入

| 输入类型 | 变量 | 必填 | 说明 |
|---------|------|------|------|
| 数据集路径 | `{DATASET_PATH}` | 是 | 基准数据集目录 |
| 数据集名称 | `{DATASET_NAME}` | 是 | 来源与版本 |
| 数据契约 | `{DATA_CONTRACT}` | 否 | 变量单位网格定义 |
| 切分配置 | `{SPLIT_CONFIG}` | 是 | 训练/验证/测试比例 |
| 目标变量 | `{TARGET_FIELDS}` | 是 | 待预测物理量列表 |
| 模型名称 | `{MODEL_NAME}` | 是 | Meta-PINN/PINN agent/PINN Transformer |
| 训练配置 | `{TRAIN_CONFIG}` | 是 | 超参数和随机种子 |

## 输出

| 步骤 | 输出产物 | 说明 |
|------|---------|------|
| s01 | dataset_manifest.json, data_contract.json, data_audit.md | 数据清单与契约 |
| s02 | train_manifest.json, validation_manifest.json, test_manifest.json, normalization.json | 切分与归一化 |
| s03 | best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt | 训练产物 |
| s04 | solution_fields/, pde_residuals/, boundary_residuals.csv | 解场与残差 |
| s05 | evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt | 验收报告 |

## 流程节点

### s01: 数据接入与契约核验

**操作**：读取{DATASET_PATH}中的{DATASET_NAME}，建立数据清单。

**检查项**：
- 文件可读性
- 样本数与可追溯性
- 输入与目标变量定义
- 单位、坐标系、网格拓扑
- 时间或工况范围
- 缺失值与使用许可

**输出**：dataset_manifest.json, data_contract.json, data_audit.md

**质量门禁**：
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏

---

### s02: 预处理与数据切分

**操作**：依据s01契约完成质控、重采样或图构建、掩膜、归一化或无量纲化。

**切分策略**：
- 按{SPLIT_CONFIG}配置（默认70/15/15）
- 以几何、完整轨迹或物理工况为单位切分
- 不得把同一轨迹的帧随机打散

**输出**：train_manifest.json, validation_manifest.json, test_manifest.json, normalization.json

**质量门禁**：
- 三份切分的对象轨迹互斥
- 仅用训练集计算变换统计量
- 边界与掩膜语义未破坏

---

### s03: 模型配置与训练

**操作**：使用{MODEL_NAME}（默认Meta-PINN、PINN agent、PINN Transformer）和{TRAIN_CONFIG}训练模型。

**训练流程**：
- 加载s02切分与统计量
- 记录代码版本、依赖、随机种子
- 记录逐轮训练验证指标
- 保存最佳权重

**可选**：提供{INIT_CHECKPOINT}时检查结构兼容性

**输出**：best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt

**质量门禁**：
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

---

### s04: 方程求解与物理残差恢复

**操作**：加载{CHECKPOINT}，在测试参数、边界和查询坐标上求解目标PDE。

**技术要点**：
- 使用自动微分或离散算子恢复导数
- 计算通量和方程残差
- 保存解场与残差场

**关键约束**：禁止只依据训练损失判定方程已求解

**输出**：solution_fields/, pde_residuals/, boundary_residuals.csv

**质量门禁**：
- 解场导数与残差均为有限值
- 边初值逐项满足门限
- 独立数值解或解析解可对照

---

### s05: 任务验收与适用域判定

**操作**：按{METRICS}评价s04结果，给出PASS/REJECT/BLOCKED结论。

**验收内容**：
- 逐变量误差（relative_L2）
- 边界误差（boundary_error）
- 守恒或方程残差（PDE_residual, conservation_error）
- 最差样本与推理成本

**外推测试**：若{RUN_OOD_TEST}为true，执行几何或工况外推测试并明确适用域

**输出**：evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt

**质量门禁**：
- 统计与物理指标同时报告
- 最差样本可追溯
- 结论含适用域限制与复核建议

## 关键参数

### 通用判据（方法层）

| 步骤 | 参数 | 判据 | 来源 | 说明 |
|------|------|------|------|------|
| s01 | 数据泄漏 | 训练/验证/测试集对象轨迹互斥 | [场景需求书s01] | 按几何或轨迹切分 |
| s02 | 统计量来源 | 仅用训练集计算 | [场景需求书s02] | 防止信息泄漏 |
| s02 | 边界语义 | 掩膜与边界未破坏 | [场景需求书s02] | 物理约束完整性 |
| s03 | 损失有限性 | 训练验证损失为有限值 | [场景需求书s03] | 发散即终止 |
| s03 | 权重可加载 | checkpoint完整可恢复 | [场景需求书s03] | 模型持久化 |
| s04 | 残差有限性 | 导数与残差均为有限值 | [场景需求书s04] | 非数值即异常 |
| s04 | 边界满足 | 边初值逐项满足门限 | [场景需求书s04] | 物理硬约束 |
| s05 | 双指标 | 统计与物理指标同时报告 | [场景需求书s05] | 不得仅凭平均误差 |

### 校准数值（PDEBench/PINNacle体系）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 切分比例 | 70/15/15 | [场景需求书s02] | 默认配置 |
| 随机种子 | 42 | [场景需求书s02/s03] | 可复现性 |
| 默认框架 | PyTorch | [场景需求书s03] | 实现依赖 |
| 默认轮数 | 100 epochs | [场景需求书s03] | 可调整 |
| 默认批大小 | 8 | [场景需求书s03] | 按显存调整 |
| 学习率 | 0.001 | [场景需求书s03] | 基准超参 |
| 早停耐心 | 15 epochs | [场景需求书s03] | 验证集不改善终止 |
| 相对L2门限 | 0.1 | [场景需求书s05] | 测试集放行阈值 |
| 推理批大小 | 8 | [场景需求书s04] | 按显存调整 |
| 计算设备 | cuda | [场景需求书s04] | 默认GPU |

## 边界与分流

| 前提条件 | 不成立时转向 |
|---------|-------------|
| 数据集格式合规 | 进行格式适配或手动定义契约 |
| 模型在训练集收敛 | 调整损失函数/网络/学习率 |
| 物理残差合理 | 回退单方程PINN或调整损失权重 |
| 域外工况需要复核 | 提交CFD专业复核 |

## 质量检查

**五步门禁汇总**：
1. s01：数据可读、变量完整、无泄漏
2. s02：切分互斥、统计量纯净、语义完整
3. s03：损失有限、权重可加载、环境可复现
4. s04：残差有限、边界满足、可对照验证
5. s05：双指标报告、最差样本追溯、适用域明确

## 回退策略

1. **数据格式问题**：s01失败时，手动定义数据契约或格式适配
2. **训练发散**：s03失败时，降低学习率、增加早停耐心、调整网络
3. **残差过大**：s04失败时，增加配点、调整损失权重
4. **验收不通过**：s05给出REJECT时，回退到更简单的模型或单方程方案

## 资源召回建议

- 当需要执行完整的自动化PINN跨方程求解流程时召回本卡片
- 配套资源：PDEBench/PINNacle数据集、Meta-PINN/PINN agent/PINN Transformer实现
- 关联卡片：cfd-automated-meta-learning-pinn-cross-equation（场景概览）

## 证据来源

[1] PINNacle: A Comprehensive Benchmark of Physics-Informed Neural Networks for Solving PDEs, arXiv:2306.08827, 2023
[2] PDEBench: An Extensive Benchmark for Scientific Machine Learning, arXiv:2202.00728, 2022
