# 物理信息扩散模型流场分布生成工作流

## 适用范围

适用于使用物理信息扩散模型完成流场分布生成任务的端到端工作流。覆盖从原始条件流场数据接入到最终任务验收的完整生命周期。每个阶段可独立执行，支持中间结果检查与回退。

## 输入

- 原始条件流场与物理残差数据集（含边界条件、几何参数、工况）
- 数据契约定义（变量、单位、网格、坐标系）
- 训练配置（超参数、随机种子、框架选择）

## 输出

- 验证通过的扩散模型 checkpoint
- 多样流场样本集与分布评估
- 物理一致性报告与适用域判定
- 可复现的环境与配置记录

## 流程节点

```
s01 数据接入与契约核验
  ↓
s02 预处理与数据切分
  ↓
s03 模型配置与训练
  ↓
s04 条件采样与物理一致性筛选
  ↓
s05 任务验收与适用域判定
```

### s01 数据接入与契约核验

**操作**：读取 {DATASET_PATH} 中的 {DATASET_NAME}，建立数据清单。检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可。

**输入**：
- {DATASET_PATH}（必填）：目录或清单文件
- {DATASET_NAME}（必填）：数据集名称，默认"条件流场与物理残差数据"
- {DATA_CONTRACT}（可选）：变量单位网格定义

**输出**：dataset_manifest.json, data_contract.json, data_audit.md

**质量门禁**：
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏

**失败处理**：缺少必填输入时返回 BLOCKED 并列出缺项，不得编造数据、权重、工况或结果。

---

### s02 预处理与数据切分

**操作**：依据 s01 契约完成质控、重采样或图构建、掩膜、归一化或无量纲化。按 {SPLIT_CONFIG} 以几何、完整轨迹或物理工况为单位切分。

**输入**：
- {SPLIT_CONFIG}（必填）：切分配置，默认 train=0.7, val=0.15, test=0.15, seed=42, group_by=geometry_or_trajectory
- {TARGET_FIELDS}（必填）：目标变量列表
- {NONDIMENSIONALIZE}（可选）：是否无量纲化，默认 true

**输出**：train_manifest.json, validation_manifest.json, test_manifest.json, normalization.json

**质量门禁**：
- 三份切分的对象轨迹互斥
- 仅用训练集计算变换统计量
- 边界与掩膜语义未破坏

**关键约束**：不得把同一轨迹的帧随机打散。为 {TARGET_FIELDS} 保存统计量与可逆变换。

---

### s03 模型配置与训练

**操作**：使用 {MODEL_NAME}（默认 Physics-informed diffusion model）和 {TRAIN_CONFIG} 训练模型。加载 s02 切分与统计量，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。

**输入**：
- {MODEL_NAME}（必填）：实现或模型注册名
- {TRAIN_CONFIG}（必填）：超参数配置
- {INIT_CHECKPOINT}（可选）：可选预训练权重

**输出**：best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt

**质量门禁**：
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

**关键约束**：若提供 {INIT_CHECKPOINT} 须检查结构兼容性。

---

### s04 条件采样与物理一致性筛选

**操作**：加载 {CHECKPOINT}，对每个测试条件生成多随机种子样本，保存采样轨迹、条件和随机种子。恢复物理量后计算边界、守恒与方程残差，剔除不合格样本并评估分布覆盖。

**输入**：
- {CHECKPOINT}（必填）：通过训练门限权重
- {DEVICE}（必填）：CPU 或 CUDA 设备
- {BATCH_SIZE}（可选）：推理批大小，默认 8

**输出**：generated_samples/, physics_filter.json, distribution_metrics.json

**质量门禁**：
- 样本条件与随机种子可追溯
- 多样性和真实性同时评价
- 物理筛选前后统计均报告

**关键约束**：禁止用单个漂亮样本代表整体性能。

---

### s05 任务验收与适用域判定

**操作**：按 {METRICS} 评价 s04 结果，至少报告逐变量误差、边界误差、守恒或方程残差、最差样本和推理成本。使用 {MAX_RELATIVE_L2} 及任务物理门限给出 PASS、REJECT 或 BLOCKED。

**输入**：
- {METRICS}（必填）：验收指标列表
- {MAX_RELATIVE_L2}（可选）：相对误差门限，默认 0.1
- {RUN_OOD_TEST}（可选）：是否外推测试，默认 true

**输出**：evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt

**质量门禁**：
- 统计与物理指标同时报告
- 最差样本可追溯
- 结论含适用域限制与复核建议

**关键约束**：不得仅凭平均误差宣称工程可用。

## 关键参数

### 通用判据

| 参数 | 说明 | 来源 |
|------|------|------|
| 切分方式 | 按几何/轨迹/工况切分，禁止帧级随机打散 | [场景需求书 s02] |
| 物理筛选 | 多种子采样 + 残差阈值 + 分布覆盖 | [场景需求书 s04] |
| 验收标准 | 统计指标 + 物理指标同时达标 | [场景需求书 s05] |
| 适用域 | 几何/工况外推测试 + CFD 复核建议 | [场景需求书 s05] |

### 校准数值

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| train/val/test | 0.7/0.15/0.15 | [场景需求书] | 默认比例 |
| random seed | 42 | [场景需求书] | 可调整 |
| epochs | 100 | [场景需求书] | 默认 |
| batch_size | 8 | [场景需求书] | 按显存调整 |
| learning_rate | 0.001 | [场景需求书] | 默认 |
| early_stopping_patience | 15 | [场景需求书] | 防过拟合 |
| MAX_RELATIVE_L2 | 0.1 | [场景需求书] | 默认阈值 |

## 边界与分流

- s01 返回 BLOCKED → 停止，列出缺项
- s02 切分泄漏 → 回到 s01 重新核验数据
- s03 训练不收敛 → 检查超参数，必要时使用 {INIT_CHECKPOINT} 微调
- s04 样本全部被物理筛选剔除 → 放宽阈值并标注置信度降级
- s05 REJECT → 回到 s03 调整训练策略或回到 s02 调整切分
- s05 BLOCKED → 停止，报告阻塞原因

## 质量检查

- 每个阶段的 quality_gate 必须通过才能进入下一阶段
- 所有中间产物（manifest、config、metrics）必须落盘且可追溯
- 最终验收需同时满足统计与物理指标

## 回退策略

- 数据质量问题 → 回到 s01 修复数据
- 训练失败 → 回到 s03 调整配置或使用预训练权重
- 物理筛选过于严格 → 放宽阈值并标注置信度
- 验收不通过 → 根据具体原因回退到对应阶段

## 资源召回建议

- 需要了解完整端到端流程时召回本卡
- 需要某个阶段的详细操作指引时召回对应 task 卡
- 需要了解场景级方法论时召回 cfd-physics-informed-diffusion-flow-field-generation

## 证据来源

[1] Physics-Informed Diffusion Models, 2024
[2] Learning Distributions of Complex Fluid Simulations with Diffusion Graph Networks, Lino et al., ICLR 2025, arXiv:2504.02843
[3] Self-Augmented Diffusion Guidance for Physics-Informed Generation, Osaka et al., 2026, arXiv:2608.26748
