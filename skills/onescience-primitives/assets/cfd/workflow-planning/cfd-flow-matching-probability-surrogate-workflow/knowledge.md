# Flow Matching 概率代理工作流

## 适用范围

本工作流定义使用 Flow matching model 构建复杂流动概率代理的完整执行流程，覆盖从数据接入到验收判定的五个阶段。适用于参数条件-流场分布配对样本的生成式概率建模任务。每个阶段有明确的输入输出契约和质量门禁，阶段间通过门禁判定决定流转或回退。

## 输入

- 参数条件与流场分布样本（目录或清单）
- 数据契约（变量名、单位、网格坐标系定义）
- 训练配置（超参数、随机种子、框架版本）
- 验收指标与门限

## 输出

- 可复现模型 checkpoint
- 生成样本集与物理筛选结果
- 验收评估报告与适用域报告
- 最终判定（PASS / REJECT / BLOCKED）

## 流程节点

### 阶段 1：数据接入与契约核验（s01）

**操作**：读取数据集，建立数据清单，核验文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可。按数据契约输出机器可读契约。

**输入**：{DATASET_PATH}, {DATASET_NAME}, {DATA_CONTRACT}
**输出**：dataset_manifest.json, data_contract.json, data_audit.md
**质量门禁**：
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏
**流转**：门禁全部通过 → 阶段 2；否则 → BLOCKED 并列出缺项

### 阶段 2：预处理与数据切分（s02）

**操作**：依据阶段 1 契约完成质控、重采样或图构建、掩膜、归一化或无量纲化。按{SPLIT_CONFIG}以几何、完整轨迹或物理工况为单位切分，不得把同一轨迹的帧随机打散。为{TARGET_FIELDS}保存统计量与可逆变换。

**输入**：{SPLIT_CONFIG}, {TARGET_FIELDS}, {NONDIMENSIONALIZE}
**输出**：train_manifest.json, validation_manifest.json, test_manifest.json, normalization.json
**质量门禁**：
- 三份切分的对象轨迹互斥
- 仅用训练集计算变换统计量
- 边界与掩膜语义未破坏
**流转**：门禁全部通过 → 阶段 3；否则 → 回退阶段 1 重新核验数据

### 阶段 3：模型配置与训练（s03）

**操作**：使用{MODEL_NAME}（默认 Flow matching model）和{TRAIN_CONFIG}训练概率代理模型。加载阶段 2 切分与统计量，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。若提供{INIT_CHECKPOINT}须检查结构兼容性。

**输入**：{MODEL_NAME}, {TRAIN_CONFIG}, {INIT_CHECKPOINT}
**输出**：best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt
**质量门禁**：
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现
**流转**：门禁全部通过 → 阶段 4；否则 → 检查数据质量与超参数，回退阶段 2 或 BLOCKED

### 阶段 4：条件采样与物理一致性筛选（s04）

**操作**：加载{CHECKPOINT}，对每个测试条件生成多随机种子样本，保存采样轨迹、条件和随机种子。恢复物理量后计算边界、守恒与方程残差，剔除不合格样本并评估分布覆盖。禁止用单个漂亮样本代表整体性能。

**输入**：{CHECKPOINT}, {DEVICE}, {BATCH_SIZE}
**输出**：generated_samples/, physics_filter.json, distribution_metrics.json
**质量门禁**：
- 样本条件与随机种子可追溯
- 多样性和真实性同时评价
- 物理筛选前后统计均报告
**流转**：门禁全部通过 → 阶段 5；否则 → 回退阶段 3 重新训练或 BLOCKED

### 阶段 5：任务验收与适用域判定（s05）

**操作**：按{METRICS}评价阶段 4 结果，至少报告逐变量误差、边界误差、守恒或方程残差、最差样本和推理成本。使用{MAX_RELATIVE_L2}及任务物理门限给出 PASS、REJECT 或 BLOCKED。若{RUN_OOD_TEST}为 true，执行几何或工况外推测试并明确适用域，不得仅凭平均误差宣称工程可用。

**输入**：{METRICS}, {MAX_RELATIVE_L2}, {RUN_OOD_TEST}
**输出**：evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt
**质量门禁**：
- 统计与物理指标同时报告
- 最差样本可追溯
- 结论含适用域限制与复核建议
**流转**：PASS → 交付；REJECT → 回退阶段 3 或 BLOCKED → 停止并报告

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 训练框架 | PyTorch | [场景需求书] | 默认框架 |
| epochs | 100 | [场景需求书] | 默认训练轮数 |
| batch_size | 8 | [场景需求书] | 默认批次大小 |
| learning_rate | 0.001 | [场景需求书] | 默认学习率 |
| early_stopping_patience | 15 | [场景需求书] | 验证集无改善提前停止 |
| 切分比例 | 0.7/0.15/0.15 | [场景需求书] | train/val/test |
| MAX_RELATIVE_L2 | 0.1 | [场景需求书] | 测试集放行阈值 |

## 边界与分流

- 阶段 1 质量门禁失败：返回 BLOCKED，不得编造数据
- 阶段 2 切分泄漏：同一轨迹帧被打散时必须重新按轨迹分组
- 阶段 3 训练不收敛：检查框架版本、依赖、随机种子；必要时降低学习率
- 阶段 4 物理筛选通过率极低：检查物理残差计算逻辑，或放宽阈值重新评估
- 阶段 5 REJECT：明确列出域外工况范围，建议 CFD 复核

## 质量检查

- 每个阶段的质量门禁必须全部通过方可流转
- 最终验收须同时报告统计误差和物理约束
- 适用域报告须明确列出工况范围限制
- 所有中间产物须可追溯（checkpoint、manifest、metrics）

## 回退策略

- 数据问题 → 回退阶段 1
- 切分问题 → 回退阶段 2
- 训练问题 → 回退阶段 3 或 BLOCKED
- 采样问题 → 回退阶段 4
- 验收不通过 → BLOCKED 并报告

## 资源召回建议

当用户需要执行完整的 Flow matching 概率代理构建流程时召回本卡片。配套资源：cfd-flow-matching-probability-surrogate-scenario（场景定义）、各阶段任务卡片（cfd-flow-matching-data-intake-contract-validation 等）。

## 证据来源

[1] Switched Flow Matching: Eliminating Singularities via Switching ODEs, 2024
[2] Physics vs Distributions: Pareto Optimal Flow Matching with Physics Constraints, 2024
[3] Dflow-SUR: Enhancing Generative Aerodynamic Inverse Design using Differentiation Throughout Flow Matching, arXiv:2512.08336, 2025
[4] GeoFunFlow-3D: A Physics-Guided Generative Flow Matching Framework for High-Fidelity 3D Aerodynamic Inference over Complex Geometries, arXiv:2604.23350, 2026
[5] Physics-Guided Generative Surrogates for Parametric Rarefied Flows with Neural-Field Auto-Decoders: A Pipeline-Level Study of Flow Matching and Diffusion, arXiv:2608.25454, 2026
