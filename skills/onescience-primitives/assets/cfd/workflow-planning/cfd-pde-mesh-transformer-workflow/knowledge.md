# 大规模网格Transformer三维流场预测工作流

## 适用范围

**触发条件**：
- 需要端到端执行百万节点PDE网格上Transformer流场预测任务
- 需要完整的数据接入→预处理→训练→推理→验收流程
- 需要每步有明确的质量门禁和输出契约

**适用场景**：
- 从零开始执行大规模网格Transformer流场预测
- 需要可复现、可审计的完整工作流
- 需要物理一致性评估和适用域判定

**不适用场景**：
- 仅需单步执行（如仅训练或仅推理）
- 已有成熟流水线只需调用
- 小规模网格问题（工作流开销过大）

## 流程概览

```
s01 数据接入与契约核验 → s02 预处理与数据切分 → s03 模型配置与训练 → s04 批量推理与物理恢复 → s05 任务验收与适用域判定
```

依赖关系：s01→s02→s03→s04→s05（线性依赖）

## Step 1：数据接入与契约核验（s01）

**目标**：接入百万节点通用三维PDE网格数据，核验样本、变量、单位、网格坐标及许可。

**输入**：
- {DATASET_PATH}：数据集路径（必填）
- {DATASET_NAME}：数据集名称与版本（必填）
- {DATA_CONTRACT}：数据契约（可选，含input_fields、target_fields、units、coordinates）

**操作**：
1. 读取数据集路径，检查文件可读性
2. 统计样本数、输入与目标变量
3. 核验单位、坐标系、网格拓扑
4. 检查时间或工况范围、缺失值
5. 检查使用许可
6. 按{DATA_CONTRACT}输出机器可读契约

**输出**：
- dataset_manifest.json：数据清单
- data_contract.json：机器可读数据契约
- data_audit.md：数据审计报告

**质量门禁**：
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏

**边界处理**：
- 缺少必填输入时返回BLOCKED并列出缺项
- 不得编造数据、权重、工况或结果

## Step 2：预处理与数据切分（s02）

**目标**：统一物理量与表示，按几何、工况或时间构造无泄漏切分。

**输入**：
- {SPLIT_CONFIG}：切分配置（必填，默认train:0.7/val:0.15/test:0.15, seed:42, group_by:geometry_or_trajectory）
- {TARGET_FIELDS}：目标变量列表（必填）
- {NONDIMENSIONALIZE}：是否无量纲化（可选，默认true）

**操作**：
1. 依据s01契约完成质控
2. 重采样或图构建
3. 掩膜处理
4. 归一化或无量纲化
5. 按{SPLIT_CONFIG}以几何、完整轨迹或物理工况为单位切分
6. 保存统计量与可逆变换

**输出**：
- train_manifest.json：训练集清单
- validation_manifest.json：验证集清单
- test_manifest.json：测试集清单
- normalization.json：归一化统计量

**质量门禁**：
- 三份切分的对象轨迹互斥
- 仅用训练集计算变换统计量
- 边界与掩膜语义未破坏

**关键约束**：
- 不得把同一轨迹的帧随机打散
- 为{TARGET_FIELDS}保存统计量与可逆变换

## Step 3：模型配置与训练（s03）

**目标**：使用Transolver、Mesh Transformer训练流场预测模型。

**输入**：
- {MODEL_NAME}：模型名称（必填，默认Transolver、Mesh Transformer）
- {TRAIN_CONFIG}：训练配置（必填，默认framework:PyTorch, epochs:100, batch_size:8, lr:0.001, seed:42, early_stopping_patience:15）
- {INIT_CHECKPOINT}：初始权重（可选）

**操作**：
1. 加载s02切分与统计量
2. 初始化模型（若提供{INIT_CHECKPOINT}须检查结构兼容性）
3. 训练循环：记录代码版本、依赖、随机种子
4. 逐轮记录训练验证指标
5. 保存最佳权重

**输出**：
- best_checkpoint.pt：最佳模型权重
- train_config.json：训练配置
- training_metrics.csv：逐轮训练验证指标
- environment.txt：环境信息

**质量门禁**：
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

**边界处理**：
- 缺少必填输入时返回BLOCKED并列出缺项
- 不得编造数据、权重、工况或结果

## Step 4：批量推理与物理恢复（s04）

**目标**：在独立测试集推理，恢复原始单位、网格和物理派生量。

**输入**：
- {CHECKPOINT}：模型权重（必填，默认best_checkpoint.pt）
- {DEVICE}：计算设备（必填，默认cuda）
- {BATCH_SIZE}：推理批大小（可选，默认8）

**操作**：
1. 加载{CHECKPOINT}及训练时数据契约
2. 在s02独立测试集上以{DEVICE}和{BATCH_SIZE}推理
3. 反归一化并恢复物理单位
4. 恢复坐标网格、边界掩膜及任务派生量
5. 保存逐样本结果和耗时

**输出**：
- predictions/：逐样本预测结果目录
- inference_manifest.json：推理清单
- timing.csv：推理耗时

**质量门禁**：
- 预测无NaN或Inf且形状单位正确
- 每个测试样本有唯一结果
- 推理未使用测试目标校正

**关键约束**：
- 禁止用测试标签修正预测

## Step 5：任务验收与适用域判定（s05）

**目标**：评估统计误差、关键物理约束、泛化能力和计算收益。

**输入**：
- {METRICS}：验收指标（必填，默认relative_L2、RMSE、conservation_residual、boundary_error）
- {MAX_RELATIVE_L2}：相对误差门限（可选，默认0.1）
- {RUN_OOD_TEST}：是否外推测试（可选，默认true）

**操作**：
1. 按{METRICS}评价s04结果
2. 报告逐变量误差、边界误差、守恒或方程残差
3. 识别最差样本
4. 报告推理成本
5. 使用{MAX_RELATIVE_L2}及任务物理门限给出PASS、REJECT或BLOCKED
6. 若{RUN_OOD_TEST}为true，执行几何或工况外推测试
7. 明确适用域边界

**输出**：
- evaluation.json：评估结果
- worst_cases.csv：最差样本详情
- applicability_report.md：适用域报告
- PASS_REJECT_BLOCKED.txt：验收结论

**质量门禁**：
- 统计与物理指标同时报告
- 最差样本可追溯
- 结论含适用域限制与复核建议

**关键约束**：
- 不得仅凭平均误差宣称工程可用
- 域外工况需经CFD复核

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 切分比例 | train:0.7/val:0.15/test:0.15 | [场景需求书] | 标准三分切分 |
| 分组策略 | geometry_or_trajectory | [场景需求书] | 按几何或轨迹切分防泄漏 |
| 归一化 | 无量纲化 | [场景需求书] | 统一跨工况量纲 |
| 验收指标 | relative_L2, RMSE, conservation_residual, boundary_error | [场景需求书] | 统计+物理双维度 |
| 相对误差门限 | 0.1 | [场景需求书] | 默认放行阈值 |
| 域外测试 | 默认开启 | [场景需求书] | 几何或工况外推 |

### 校准数值（场景专属）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 网格规模 | 百万节点级 | [场景需求书] | 以下数值来自CFD_S006场景，供量级校准；其他体系需以自身证据重新锚定 |
| 模型 | Transolver, Mesh Transformer | [场景需求书] | 通用神经PDE求解器 |
| 训练轮数 | 100 | [场景需求书] | 默认最大轮数 |
| 批大小 | 8 | [场景需求书] | 默认训练批大小 |
| 学习率 | 0.001 | [场景需求书] | 默认学习率 |
| 早停耐心 | 15 | [场景需求书] | 验证损失不改善容忍轮数 |
| 随机种子 | 42 | [场景需求书] | 可复现性保证 |

## 边界与分流

| 前提条件 | 不成立时的改道方案 |
|----------|-------------------|
| 数据为百万节点PDE网格 | 小规模→传统CFD或轻量模型；规则网格→FFT方法 |
| 网格为非结构化 | 结构化→U-Net/FNO等规则网格架构 |
| 需要物理一致性 | 纯数据驱动→标准MLP/CNN，标注物理不可信 |
| 域外工况需CFD复核 | 无CFD能力→限制域内使用 |
| HPC不可用 | 本地GPU→减小模型/批大小，延长训练 |
| 模型不收敛 | 调超参或降级基线模型 |

## 质量检查

| 检查点 | 标准 | 失败处理 |
|--------|------|----------|
| 数据完整性 | 文件可读、变量完整 | BLOCKED |
| 切分无泄漏 | 对象轨迹互斥 | 重新切分 |
| 训练收敛 | 损失有限、权重可加载 | 调超参 |
| 推理正确 | 无NaN/Inf、单位正确 | 检查恢复逻辑 |
| 物理一致性 | 守恒/边界误差合理 | 标注不可信区域 |
| 适用域明确 | 有OOD结论 | 不可宣称可用 |

## 资源召回建议

当用户需求涉及以下场景时应召回本卡片：
- 需要端到端执行大规模网格Transformer流场预测
- 需要完整的五步工作流定义
- 需要每步的质量门禁和输出契约

配套资源建议：
- `cfd-pde-large-scale-mesh-transformer-flow-prediction`：场景级概述卡
- `cfd-mesh-transformer-data-intake-contract`：数据接入步骤卡
- `cfd-mesh-transformer-preprocessing-split`：预处理步骤卡
- `cfd-mesh-transformer-model-training`：训练步骤卡
- `cfd-mesh-transformer-inference-recovery`：推理步骤卡
- `cfd-mesh-transformer-evaluation-applicability`：评估步骤卡

## 证据来源

[1] "Transolver: A Fast Transformer Solver for PDEs on General Geometries", 2024
[2] "Transolver++: An Accurate Neural Solver for PDEs on Million-Scale Geometries", 2024

注：本卡片知识来源为场景需求书CFD_S006的结构化字段，未执行外部文献检索。
