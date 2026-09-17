# 大规模网格Transformer三维流场预测

## 适用范围

面向百万节点通用三维PDE网格数据，使用Transformer架构完成流场预测的完整工作流。适用于需要对大规模非结构化网格上的三维流场进行快速推断、同时要求物理一致性评估和适用域判定的研究或工程场景。

**触发条件**：
- 需要对百万节点级别的三维非结构化网格PDE数据进行流场预测
- 需要Transformer架构的神经PDE求解器替代或加速传统CFD计算
- 需要物理一致性评估（守恒残差、边界误差）和适用域判定

**适用场景**：
- 三维流体力学问题的快速预测（如湍流、层流、多相流）
- 大规模网格上的参数化PDE求解
- 需要推理加速的工程设计优化循环
- 需要物理约束的科学机器学习应用

**不适用场景**：
- 小规模规则网格上的简单PDE（传统数值方法更高效）
- 非流体类PDE问题（除非方法已适配）
- 纯数据驱动无物理约束的黑箱预测（不符合物理一致性要求）
- 域外工况未经CFD复核直接部署

## 输入

| 输入 | 类型 | 必填 | 说明 |
|------|------|------|------|
| {DATASET_PATH} | doc | 是 | 百万节点通用三维PDE网格数据集路径 |
| {DATASET_NAME} | str | 是 | 数据集名称与版本 |
| {DATA_CONTRACT} | object | 否 | 变量单位、网格定义的契约 |
| {SPLIT_CONFIG} | object | 是 | 切分比例、种子、分组策略 |
| {TARGET_FIELDS} | list[str] | 是 | 待预测物理量列表 |
| {MODEL_NAME} | str | 是 | 模型名称（如Transolver、Mesh Transformer） |
| {TRAIN_CONFIG} | object | 是 | 训练超参数配置 |
| {CHECKPOINT} | doc | 是 | 模型权重路径 |
| {DEVICE} | str | 是 | 计算设备（CPU/CUDA） |
| {BATCH_SIZE} | int | 否 | 推理批大小 |
| {METRICS} | list[str] | 是 | 验收指标列表 |
| {MAX_RELATIVE_L2} | float | 否 | 相对误差门限（默认0.1） |
| {RUN_OOD_TEST} | bool | 否 | 是否执行域外测试 |

## 输出

| 输出 | 格式 | 说明 |
|------|------|------|
| dataset_manifest.json | JSON | 数据清单 |
| data_contract.json | JSON | 机器可读数据契约 |
| data_audit.md | Markdown | 数据审计报告 |
| train/validation/test_manifest.json | JSON | 切分清单 |
| normalization.json | JSON | 归一化统计量 |
| best_checkpoint.pt | PyTorch | 最佳模型权重 |
| train_config.json | JSON | 训练配置 |
| training_metrics.csv | CSV | 逐轮训练验证指标 |
| predictions/ | 目录 | 逐样本预测结果 |
| inference_manifest.json | JSON | 推理清单 |
| timing.csv | CSV | 推理耗时 |
| evaluation.json | JSON | 评估结果 |
| worst_cases.csv | CSV | 最差样本详情 |
| applicability_report.md | Markdown | 适用域报告 |
| PASS_REJECT_BLOCKED.txt | Text | 验收结论 |

## 流程节点

### Step 1：数据接入与契约核验（s01）
- **操作**：接入百万节点通用三维PDE网格数据，核验样本、变量、单位、网格坐标及许可
- **参数**：DATASET_PATH、DATASET_NAME、DATA_CONTRACT
- **工具**：数据读取库（H5py/NetCDF4/PyTorch Geometric）
- **质量门禁**：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏
- **产出**：dataset_manifest.json、data_contract.json、data_audit.md

### Step 2：预处理与数据切分（s02）
- **操作**：统一物理量与表示，按几何、工况或时间构造无泄漏切分
- **参数**：SPLIT_CONFIG（train:0.7/val:0.15/test:0.15, seed:42, group_by:geometry_or_trajectory）、TARGET_FIELDS、NONDIMENSIONALIZE
- **工具**：数据处理库（NumPy/Pandas/PyTorch）
- **质量门禁**：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏
- **产出**：train/validation/test_manifest.json、normalization.json

### Step 3：模型配置与训练（s03）
- **操作**：使用Transolver、Mesh Transformer训练流场预测模型
- **参数**：MODEL_NAME、TRAIN_CONFIG（framework:PyTorch, epochs:100, batch_size:8, lr:0.001, seed:42, early_stopping_patience:15）、INIT_CHECKPOINT
- **工具**：PyTorch框架、模型实现代码
- **质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现
- **产出**：best_checkpoint.pt、train_config.json、training_metrics.csv、environment.txt

### Step 4：批量推理与物理恢复（s04）
- **操作**：在独立测试集推理，恢复原始单位、网格和物理派生量
- **参数**：CHECKPOINT、DEVICE、BATCH_SIZE
- **工具**：PyTorch推理引擎
- **质量门禁**：预测无NaN或Inf且形状单位正确；每个测试样本有唯一结果；推理未使用测试目标校正
- **产出**：predictions/、inference_manifest.json、timing.csv

### Step 5：任务验收与适用域判定（s05）
- **操作**：评估统计误差、关键物理约束、泛化能力和计算收益
- **参数**：METRICS（relative_L2、RMSE、conservation_residual、boundary_error）、MAX_RELATIVE_L2、RUN_OOD_TEST
- **工具**：评估脚本
- **质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议
- **产出**：evaluation.json、worst_cases.csv、applicability_report.md、PASS_REJECT_BLOCKED.txt

## 关键参数

### 通用判据（方法层）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 切分比例 | train:0.7/val:0.15/test:0.15 | 场景需求书 | 标准三分切分比例 |
| 分组策略 | geometry_or_trajectory | 场景需求书 | 按几何或完整轨迹切分，防止泄漏 |
| 归一化 | 无量纲化 | 场景需求书 | 统一跨工况量纲 |
| 验收指标 | relative_L2, RMSE, conservation_residual, boundary_error | 场景需求书 | 统计+物理双维度评估 |
| 相对误差门限 | 0.1（默认） | 场景需求书 | 测试集放行阈值 |
| 域外测试 | 默认开启 | 场景需求书 | 几何或工况外推测试 |

### 校准数值（场景专属）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 网格规模 | 百万节点级 | 场景需求书 | 以下数值来自CFD_S006场景，供量级校准；其他体系需以自身证据重新锚定 |
| 模型 | Transolver, Mesh Transformer | 场景需求书 | 通用神经PDE求解器 |
| 训练轮数 | 100 | 场景需求书 | 默认最大训练轮数 |
| 批大小 | 8 | 场景需求书 | 默认训练批大小 |
| 学习率 | 0.001 | 场景需求书 | 默认学习率 |
| 早停耐心 | 15 | 场景需求书 | 验证损失不改善的容忍轮数 |
| 随机种子 | 42 | 场景需求书 | 可复现性保证 |

## 边界与分流

| 前提条件 | 不成立时的改道方案 |
|----------|-------------------|
| 数据集为百万节点级三维PDE网格 | 小规模网格→考虑传统CFD方法或轻量级模型；规则网格→考虑FFT-based方法 |
| 网格为非结构化格式 | 结构化网格→考虑U-Net或FNO等规则网格专用架构 |
| 需要物理一致性约束 | 纯数据驱动需求→考虑标准MLP/CNN，但需标注物理不可信 |
| 域外工况需要CFD复核 | 无CFD能力→限制模型仅在训练域内使用，明确标注适用边界 |
| HPC资源不可用 | 本地GPU训练→减小模型规模和批大小，延长训练时间 |
| 模型收敛失败 | 调整学习率/批大小/模型复杂度；降级为基线模型比较 |

## 质量检查

| 检查点 | 验证标准 | 失败处理 |
|--------|----------|----------|
| 数据完整性 | 文件可读、样本可追溯、变量单位完整 | 返回BLOCKED，列出缺项 |
| 切分无泄漏 | 三份切分对象轨迹互斥 | 重新切分，检查分组逻辑 |
| 训练收敛 | 损失为有限值、最佳权重可加载 | 调整超参数或降级 |
| 推理正确性 | 无NaN/Inf、形状单位正确、未用测试标签 | 检查反归一化和恢复逻辑 |
| 物理一致性 | 守恒残差、边界误差在合理范围 | 标注物理不可信区域 |
| 适用域明确 | 有OOD测试结论、有复核建议 | 不得仅凭平均误差宣称可用 |

## 回退策略

1. **数据不足**：降级为小规模验证，标注样本量限制
2. **模型不收敛**：切换为基线模型（如MLP）进行对比，标注方法局限
3. **物理约束违反严重**：引入物理信息损失函数（PINN-like）重新训练
4. **HPC不可用**：本地单卡训练，减小模型规模，延长训练时间
5. **域外性能差**：限制适用域，增加域内测试覆盖

## 资源召回建议

当用户需求涉及以下场景时应召回本卡片：
- 大规模非结构化网格上的流场预测
- Transformer架构用于PDE求解
- 需要物理一致性评估的神经流场预测
- 需要适用域判定的工程部署

配套资源建议：
- onescience-primitives中的cfd领域数据集规范
- onescience-primitives中的CFD工作流规划卡
- onescience-runtime中的计算执行技能

## 证据来源

[1] "Transolver: A Fast Transformer Solver for PDEs on General Geometries", 2024
[2] "Transolver++: An Accurate Neural Solver for PDEs on Million-Scale Geometries", 2024

注：本卡片知识来源为场景需求书CFD_S006的结构化字段，未执行外部文献检索。论文证据仅提供标题信息，具体参数值均来自场景需求书。
