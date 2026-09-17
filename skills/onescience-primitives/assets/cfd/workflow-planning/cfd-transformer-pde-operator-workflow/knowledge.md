# Transformer PDE算子预训练与微调工作流

## 适用范围

本工作流定义了基于Transformer架构的PDE算子学习从数据接入到验收的端到端流程。适用于需要在多方程多网格数据上训练通用PDE求解器，并微调到特定下游任务的场景。工作流支持PDE Transformer、Universal Physics Transformer等主流架构，覆盖CFD领域的常见PDE类型。

## 输入

- 多方程多网格预训练数据集（路径、名称、数据契约）
- 切分配置（比例、种子、切分单位）
- 训练配置（模型名、超参数、初始权重）
- 推理配置（设备、批大小）
- 验收配置（指标、门限、OOD测试开关）

## 输出

- 数据清单与契约（dataset_manifest.json, data_contract.json）
- 切分与归一化产物（train/val/test manifests, normalization.json）
- 训练产物（best_checkpoint.pt, training_metrics.csv）
- 推理产物（predictions/, inference_manifest.json）
- 验收报告（evaluation.json, applicability_report.md, PASS_REJECT_BLOCKED.txt）

## 流程节点

### s01 数据接入与契约核验
- **操作**：读取数据集，验证文件可读性、样本数、变量定义、单位、坐标系、网格拓扑、时间/工况范围、缺失值、使用许可
- **输出**：dataset_manifest.json, data_contract.json, data_audit.md
- **质量门禁**：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏
- **阻塞条件**：缺少必填输入时返回BLOCKED并列出缺项

### s02 预处理与数据切分
- **操作**：质控、重采样/图构建、掩膜、归一化或无量纲化；按几何/轨迹/工况切分
- **依赖**：s01
- **输出**：train_manifest.json, validation_manifest.json, test_manifest.json, normalization.json
- **质量门禁**：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏
- **关键约束**：不得把同一轨迹的帧随机打散；保存统计量与可逆变换

### s03 模型配置与训练
- **操作**：加载s02切分与统计量，使用指定模型训练，记录代码版本、依赖、随机种子、逐轮指标与最佳权重
- **依赖**：s02
- **输出**：best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt
- **质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现
- **可选**：若提供初始权重需检查结构兼容性

### s04 批量推理与物理恢复
- **操作**：加载checkpoint及数据契约，在独立测试集上推理，反归一化恢复物理单位、坐标网格、边界掩膜及派生量
- **依赖**：s03
- **输出**：predictions/, inference_manifest.json, timing.csv
- **质量门禁**：预测无NaN/Inf且形状单位正确；每个测试样本有唯一结果；推理未使用测试目标校正

### s05 任务验收与适用域判定
- **操作**：按验收指标评价结果，报告逐变量误差、边界误差、守恒/方程残差、最差样本、推理成本；执行几何/工况外推测试
- **依赖**：s04
- **输出**：evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt
- **质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议
- **判定逻辑**：使用MAX_RELATIVE_L2及任务物理门限给出PASS、REJECT或BLOCKED

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 切分比例 | train:0.7, val:0.15, test:0.15 | 场景默认 | 可根据数据量调整 |
| 切分单位 | geometry_or_trajectory | 场景默认 | 按几何体或完整轨迹切分，防止泄漏 |
| 无量纲化 | true | 场景默认 | 统一跨工况量纲 |
| 训练框架 | PyTorch | 场景默认 | 标准框架 |
| epochs | 100 | 场景默认 | 可根据收敛调整 |
| batch_size | 8 | 场景默认 | 受显存限制 |
| learning_rate | 0.001 | 场景默认 | Adam优化器 |
| early_stopping_patience | 15 | 场景默认 | 防止过拟合 |
| 验收指标 | relative_L2, RMSE, conservation_residual, boundary_error | 场景默认 | 统计+物理双维度 |
| MAX_RELATIVE_L2 | 0.1 | 场景默认 | 测试集放行阈值 |
| RUN_OOD_TEST | true | 场景默认 | 测试域外工况 |

## 边界与分流

- **数据格式不兼容**：调用onescience-data-standardizer预处理
- **显存不足**：减小batch_size或启用梯度累积
- **收敛失败**：调整学习率或换用更简单模型
- **物理约束违反**：引入PINN损失或检查数据质量
- **域外外推失败**：明确适用域边界，标记需CFD复核

## 质量检查

每个阶段有独立质量门禁，前一阶段未通过不得进入下一阶段。最终验收需同时满足统计指标和物理指标。

## 回退策略

训练不收敛→回退至更简单模型；物理约束不满足→回退至纯数值解；适用域过窄→扩大预训练数据。

## 资源召回建议

当用户需要端到端的PDE算子学习流程编排时，召回本卡片。配合具体任务卡（如数据接入、训练、推理等）使用。

## 证据来源

[1] PDE-Transformer_ Efficient and Versatile Transformers for Physics Simulations
[2] Universal Physics Transformers_ A Framework For Efficiently Scaling Neural Operators
