# GAN与正规化流湍流降阶生成工作流

## 适用范围

本工作流适用于使用 GAN 或 Normalizing Flow 进行湍流降阶生成的端到端任务执行，覆盖从数据接入到任务验收的完整流水线。适用于湍流快照与低维潜变量数据的生成建模。

**触发条件**：
- 需要使用 GAN 或 Normalizing Flow 构建湍流降阶生成模型
- 数据包含湍流快照与低维潜变量
- 需要产出可复现模型、物理一致性评估和适用域报告

**不适用场景**：
- 非生成式降阶建模（如 POD、DMD 等线性方法）
- 单次推理无训练需求
- 数据不包含湍流特征

## 输入

- 湍流快照与低维潜变量数据（{DATASET_PATH}、{DATASET_NAME}）
- 数据契约模板（{DATA_CONTRACT}，可选）
- 切分配置（{SPLIT_CONFIG}）
- 训练配置（{TRAIN_CONFIG}）
- 验收指标与门限（{METRICS}、{MAX_RELATIVE_L2}）

## 输出

- 数据清单与契约（dataset_manifest.json、data_contract.json、data_audit.md）
- 切分清单与归一化参数（train_manifest.json、validation_manifest.json、test_manifest.json、normalization.json）
- 训练产物（best_checkpoint.pt、train_config.json、training_metrics.csv、environment.txt）
- 采样与筛选结果（generated_samples/、physics_filter.json、distribution_metrics.json）
- 验收报告（evaluation.json、worst_cases.csv、applicability_report.md、PASS_REJECT_BLOCKED.txt）

## 流程节点

### Step 1：数据接入与契约核验
- **操作**：接入湍流快照与低维潜变量数据，核验样本、变量、单位、网格坐标及许可
- **参数**：{DATASET_PATH}、{DATASET_NAME}、{DATA_CONTRACT}
- **工具**：数据读取库、契约验证脚本
- **质量门禁**：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏
- **输出**：dataset_manifest.json、data_contract.json、data_audit.md

### Step 2：预处理与数据切分
- **操作**：统一物理量与表示，按几何、工况或时间构造无泄漏切分
- **参数**：{SPLIT_CONFIG}（默认 train:0.7, val:0.15, test:0.15, seed:42, group_by:geometry_or_trajectory）、{TARGET_FIELDS}、{NONDIMENSIONALIZE}
- **工具**：数据预处理库、切分工具
- **质量门禁**：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏
- **输出**：train_manifest.json、validation_manifest.json、test_manifest.json、normalization.json

### Step 3：模型配置与训练
- **操作**：使用 GAN 或 Normalizing Flow 训练湍流降阶生成模型
- **参数**：{MODEL_NAME}（默认 GAN/Normalizing flow）、{TRAIN_CONFIG}（默认 PyTorch, epochs:100, batch_size:8, lr:0.001, seed:42, early_stopping_patience:15）、{INIT_CHECKPOINT}（可选）
- **工具**：PyTorch 等深度学习框架
- **质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现
- **输出**：best_checkpoint.pt、train_config.json、training_metrics.csv、environment.txt

### Step 4：条件采样与物理一致性筛选
- **操作**：按工况生成多样流场样本并依据物理残差筛选
- **参数**：{CHECKPOINT}（默认 best_checkpoint.pt）、{DEVICE}（默认 cuda）、{BATCH_SIZE}（默认 8）
- **工具**：推理引擎、物理残差计算脚本
- **质量门禁**：样本条件与随机种子可追溯；多样性和真实性同时评价；物理筛选前后统计均报告
- **输出**：generated_samples/、physics_filter.json、distribution_metrics.json

### Step 5：任务验收与适用域判定
- **操作**：评估统计误差、关键物理约束、泛化能力和计算收益
- **参数**：{METRICS}（默认 distribution_distance, diversity, physics_residual, coverage）、{MAX_RELATIVE_L2}（默认 0.1）、{RUN_OOD_TEST}（默认 true）
- **工具**：评估脚本、可视化工具
- **质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议
- **输出**：evaluation.json、worst_cases.csv、applicability_report.md、PASS_REJECT_BLOCKED.txt

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 数据切分比例 | train:0.7, val:0.15, test:0.15 | [场景需求书] | 默认数据划分 |
| 切分分组依据 | geometry_or_trajectory | [场景需求书] | 按几何或轨迹切分防止泄漏 |
| 训练框架 | PyTorch | [场景需求书] | 默认框架 |
| 默认 epochs | 100 | [场景需求书] | 训练轮数 |
| 默认 batch_size | 8 | [场景需求书] | 批大小 |
| 默认学习率 | 0.001 | [场景需求书] | 优化器参数 |
| 默认早停耐心 | 15 | [场景需求书] | 早停轮数 |
| 默认随机种子 | 42 | [场景需求书] | 复现性 |
| 默认相对误差门限 | 0.1 | [场景需求书] | 验收阈值 |
| 默认设备 | cuda | [场景需求书] | 推理设备 |
| 验收指标 | distribution_distance, diversity, physics_residual, coverage | [场景需求书] | 多维度评估 |

## 边界与分流

**工作流级别降级策略**：

1. **Step 1 数据不可用** → BLOCKED，返回缺失项清单
2. **Step 2 切分异常** → 检查分组配置，调整 group_by 或切分比例
3. **Step 3 训练不收敛** → 调整超参、切换 GAN↔Normalizing Flow、或使用预训练权重微调
4. **Step 4 物理筛选通过率过低** → 放宽物理门限或增强物理约束训练
5. **Step 5 验收不通过** → 根据失败指标定向修复（增加数据、调整模型、添加物理约束）

## 质量检查

**工作流级验证**：
- 每步产物可被下游步骤正确消费
- 全流程随机种子链可追溯
- 训练/验证/测试严格无泄漏
- 物理一致性筛选在最终验收前执行
- 最差样本可追溯到具体工况和随机种子

## 回退策略

**全链路失败替代方案**：
1. GAN/Normalizing Flow 均失败 → 回退到 POD 等线性降阶方法
2. 物理一致性无法满足 → 回退到传统 CFD 计算
3. 适用域判定不确定 → 标记为"需 CFD 复核"并限制使用

## 资源召回建议

**何时应召回本卡片**：
- 需要执行 GAN 或 Normalizing Flow 湍流降阶生成的完整工作流
- 需要五阶段流水线的步骤级指导和质量门禁

**配套资源**：
- cfd-gan-normalizing-flow-data-ingestion-contract-validation（Step 1 任务卡）
- cfd-gan-normalizing-flow-preprocessing-splitting（Step 2 任务卡）
- cfd-gan-normalizing-flow-model-training（Step 3 任务卡）
- cfd-gan-normalizing-flow-conditional-sampling-physics-filter（Step 4 任务卡）
- cfd-gan-normalizing-flow-task-acceptance-applicability（Step 5 任务卡）
- cfd-gan-normalizing-flow-turbulence-rom-scenario（场景卡）

## 证据来源

[1] IG-GAN: A Generative Adversarial Network for Aerodynamic Data Generation Based on Intrinsic Geometry, arXiv:2607.11497, 2026
[2] Generative Adversarial Reduced Order Modeling, arXiv:2305.15881, 2023
[3] Enforcing statistical constraints in generative adversarial networks for modeling chaotic dynamical systems, arXiv:1905.06841, 2019
