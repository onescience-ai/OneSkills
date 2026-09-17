# 多孔与复杂输运流动场数据驱动预测工作流

## 适用范围

**触发条件**：
- 需要从多孔介质 CFD 数据端到端构建数据驱动代理模型
- 需要完整的数据接入、预处理、训练、后验验证和验收流程
- 需要产出可复现模型和适用域报告

**适用场景**：
- 多孔介质微流动与输运过程的 CNN surrogate 或 Neural differential equation 训练
- 需要将训练好的模型嵌入 RANS/LES 求解器进行后验验证
- 需要完整的工作流编排和质量门禁

**不适用场景**：
- 仅需数据预处理或仅需模型训练的片段式任务
- 不涉及后验 CFD 耦合的纯数据回归任务

## 输入

- 多孔介质 CFD 数据集路径与名称
- 数据契约（可选）
- 切分配置
- 训练配置

## 输出

- 工作流产物集：dataset_manifest.json, data_contract.json, data_audit.md, train/validation/test manifests, normalization.json, best_checkpoint.pt, training_metrics.csv, apriori_closure/, aposteriori_fields/, solver_stability.csv, evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt

## 流程节点

### Step 1：数据接入与契约核验
- **操作**：接入 CFD 数据，核验样本、变量、单位、网格坐标
- **输入**：{DATASET_PATH}, {DATASET_NAME}, {DATA_CONTRACT}
- **输出**：dataset_manifest.json, data_contract.json, data_audit.md
- **质量门禁**：数据可读且样本可追溯；变量单位坐标完整；无训练测试泄漏

→ Step 2

### Step 2：预处理与数据切分
- **操作**：统一物理量表示，按几何/工况/时间无泄漏切分
- **输入**：{SPLIT_CONFIG}, {TARGET_FIELDS}, {NONDIMENSIONALIZE}
- **输出**：train/validation/test manifests, normalization.json
- **质量门禁**：切分互斥；仅用训练集计算统计量；边界语义未破坏

→ Step 3

### Step 3：模型配置与训练
- **操作**：训练 CNN surrogate 和 Neural differential equation
- **输入**：{MODEL_NAME}, {TRAIN_CONFIG}, {INIT_CHECKPOINT}
- **输出**：best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt
- **质量门禁**：损失有限值；权重可重载；随机种子可复现

→ Step 4

### Step 4：闭合项预测与后验 CFD 耦合
- **操作**：先验评估闭合项，嵌入 RANS/LES 后验推进
- **输入**：{CHECKPOINT}, {DEVICE}, {BATCH_SIZE}
- **输出**：apriori_closure/, aposteriori_fields/, solver_stability.csv
- **质量门禁**：闭合张量满足约束；后验无发散；均值剖面与能谱经验证

→ Step 5

### Step 5：任务验收与适用域判定
- **操作**：评估统计误差、物理约束、泛化能力和计算收益
- **输入**：{METRICS}, {MAX_RELATIVE_L2}, {RUN_OOD_TEST}
- **输出**：evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt
- **质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制

## 关键参数

### 通用判据

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 工作流阶段数 | 5 | [场景需求书] | 数据接入→预处理→训练→后验→验收 |
| 切分策略 | 按几何/工况/时间分组 | [3][4] | 防止数据泄漏的核心策略 |
| 后验验证方式 | 先验误差 + RANS/LES 后验推进 | [2][3] | 双层验证确保物理一致性 |
| 验收指标 | closure RMSE, mean profile error, spectrum error, stability horizon | [场景需求书] | 统计与物理双维度验收 |
| 适用域判定 | 外推测试 + 领域专家复核 | [1][2] | 域外工况必须经 CFD 复核 |

### 校准数值

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认 train/val/test 比例 | 0.7/0.15/0.15 | [场景需求书] | 可根据数据量调整 |
| 默认随机种子 | 42 | [场景需求书] | 可复现性保证 |
| 默认学习率 | 0.001 | [场景需求书] | 可根据收敛情况调整 |
| 默认 epochs | 100 | [场景需求书] | 配合早停使用 |

> 以上数值来自 CFD_S077 场景需求书，供量级校准；其他体系需以自身证据重新锚定。

## 边界与分流

- **数据不可读或字段缺失**：在 Step 1 返回 BLOCKED，列出缺项
- **切分配置不合理**：在 Step 2 调整配置或增加数据
- **训练不收敛**：在 Step 3 调整超参数或简化模型
- **后验求解器发散**：在 Step 4 回退到先验评估
- **验收不通过**：在 Step 5 给出 REJECT 结论，建议数据增强或模型改进

## 质量检查

- 每个 Step 有独立的质量门禁，必须通过后才能进入下一步
- 最终验收必须同时满足统计误差和物理一致性要求
- 适用域报告必须包含域外工况的复核建议

## 回退策略

- 数据层问题：要求用户补充数据或修正数据契约
- 训练层问题：调整超参数或简化模型架构
- 后验层问题：回退到先验评估，仅报告闭合项精度
- 验收层问题：给出 REJECT 结论并提供改进建议

## 资源召回建议

当用户需要了解多孔介质数据驱动预测的完整流程时召回本卡。配套召回 scenario 卡 `cfd-porous-media-data-driven-prediction` 了解场景背景，召回各 task 卡了解步骤细节。

## 证据来源

[1] "Data-Driven Design Optimization of Streaming-Potential-Mediated Electrokinetic Transport of Viscoelastic Fluids in Microchannels", arXiv:2608.29939, 2026
[2] "Advances in Scientific Machine Learning for Coupled Fluid Flow and Transport", arXiv:2606.19562, 2026
[3] "Online Gate-Driven Flow Control in Resin Transfer Moulding Using a Neural-Network Surrogate", arXiv:2608.29521, 2026
[4] "Turbulent Microscale Flow Field Prediction In Porous Media Using Convolutional Neural Networks", 2026
