# 可迁移参数化ROM端到端工作流

## 适用范围

本卡描述从原始跨几何CFD数据到可部署可迁移ROM的完整工作流。适用于需要构建跨几何参数、支持稀疏传感器输入的降阶模型，并要求物理一致性验证与适用域判定的CFD任务。

## 输入

- 跨几何参数CFD仿真数据集（含流场变量、网格、几何参数标签）
- 稀疏监测数据（有限传感器位置的采样）
- 数据契约（变量、单位、坐标系定义，可选，s01可自动生成）

## 输出

- 训练好的可迁移ROM模型权重（best_checkpoint.pt）
- 独立测试集推理结果（含物理单位恢复）
- 验收报告（evaluation.json, worst_cases.csv, applicability_report.md）
- PASS/REJECT/BLOCKED判定文件

## 流程节点

```
s01 数据接入与契约核验 → s02 预处理与数据切分 → s03 模型配置与训练 → s04 批量推理与物理恢复 → s05 任务验收与适用域判定
```

### s01 数据接入与契约核验

**操作**：读取数据集，检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可。
**输入**：{DATASET_PATH}, {DATASET_NAME}, {DATA_CONTRACT}
**输出**：dataset_manifest.json, data_contract.json, data_audit.md
**质量门禁**：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏
**异常处理**：缺少必填输入时返回BLOCKED并列出缺项，不得编造数据

### s02 预处理与数据切分

**操作**：依据s01契约完成质控、重采样或图构建、掩膜、归一化或无量纲化。按几何、完整轨迹或物理工况为单位切分。
**输入**：{SPLIT_CONFIG}, {TARGET_FIELDS}, {NONDIMENSIONALIZE}
**输出**：train_manifest.json, validation_manifest.json, test_manifest.json, normalization.json
**质量门禁**：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏
**关键约束**：不得把同一轨迹的帧随机打散；为{TARGET_FIELDS}保存统计量与可逆变换

### s03 模型配置与训练

**操作**：使用Transferable ROM或Shallow recurrent decoder，加载s02切分与统计量，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。
**输入**：{MODEL_NAME}, {TRAIN_CONFIG}, {INIT_CHECKPOINT}
**输出**：best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt
**质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现
**异常处理**：若提供{INIT_CHECKPOINT}须检查结构兼容性；缺少必填输入时返回BLOCKED

### s04 批量推理与物理恢复

**操作**：加载{CHECKPOINT}及训练时数据契约，在独立测试集上推理。反归一化并恢复物理单位、坐标网格、边界掩膜及任务派生量。
**输入**：{CHECKPOINT}, {DEVICE}, {BATCH_SIZE}
**输出**：predictions/, inference_manifest.json, timing.csv
**质量门禁**：预测无NaN或Inf且形状单位正确；每个测试样本有唯一结果；推理未使用测试目标校正

### s05 任务验收与适用域判定

**操作**：按{METRICS}评价s04结果，至少报告逐变量误差、边界误差、守恒或方程残差、最差样本和推理成本。执行几何或工况外推测试并明确适用域。
**输入**：{METRICS}, {MAX_RELATIVE_L2}, {RUN_OOD_TEST}
**输出**：evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt
**质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议
**关键约束**：不得仅凭平均误差宣称工程可用；域外工况需经CFD复核

## 关键参数

### 通用判据

| 参数 | 判据 | 来源 | 说明 |
|------|------|------|------|
| 数据可读性 | 所有文件可读、样本可追溯 | s01质量门禁 | 首要检查项 |
| 切分互斥性 | 三份切分的对象轨迹互斥 | s02质量门禁 | 防止数据泄漏的核心保障 |
| 统计量来源 | 仅用训练集计算 | s02质量门禁 | 防止信息泄漏 |
| 损失有限性 | 训练/验证损失均为有限值 | s03质量门禁 | 训练过程健康指标 |
| 权重可加载 | best_checkpoint.pt可重新加载 | s03质量门禁 | 产物有效性验证 |
| 推理完整性 | 无NaN/Inf、形状单位正确 | s04质量门禁 | 推理产物可用性 |
| 指标完备性 | 统计+物理指标同时报告 | s05质量门禁 | 评估全面性 |
| 适用域明确 | 含限制与复核建议 | s05质量门禁 | 部署安全性 |

### 校准数值（来自场景需求书默认配置）

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 切分比例 | 0.7/0.15/0.15 | s02 | train/val/test |
| 默认框架 | PyTorch | s03 | 其他体系需重新锚定 |
| 默认Epochs | 100 | s03 | 其他体系需重新锚定 |
| 默认Batch Size | 8 | s03 | 其他体系需重新锚定 |
| 默认学习率 | 0.001 | s03 | 其他体系需重新锚定 |
| Early Stopping Patience | 15 | s03 | 其他体系需重新锚定 |
| 相对L2门限 | 0.1 | s05 | 默认放行阈值 |

## 边界与分流

- 数据接入阶段发现缺项 → BLOCKED，列出缺项清单
- 训练过程出现非有限损失 → 终止训练，检查数据与配置
- 推理结果包含NaN/Inf → 判定推理失败，需检查模型与数据
- 相对L2超门限 → REJECT，需调整模型或数据策略
- 域外泛化不足 → 标注适用域限制，域外需CFD复核
- 权重无法加载 → 判定产物无效，需重新训练

## 质量检查

每个阶段的质量门禁形成链式保障：
- s01：数据完整性（可读性、变量、单位、坐标）
- s02：切分正确性（互斥、统计量来源、语义保持）
- s03：训练健康性（有限损失、权重可加载、可复现）
- s04：推理正确性（无异常值、形状单位、无泄漏）
- s05：验收全面性（统计+物理、最差样本、适用域）

## 回退策略

- s01失败：补充缺失数据或修正数据格式
- s02失败：调整切分策略或重新定义分组依据
- s03失败：调整超参数、更换模型架构、增加数据
- s04失败：检查推理代码与数据契约一致性
- s05失败：根据评估结果回到对应阶段修复

## 资源召回建议

当任务需要完整的可迁移ROM构建与部署流程时召回本卡片。配合场景级卡片（cfd-transferable-rom-realtime-monitoring-scenario）使用。

## 证据来源

[1] Real-Time Monitoring of MHD Liquid Metal Flows with Shallow Recurrent Decoders, arxiv:2608.28366, 2026
[2] Non-intrusive, transferable model for coupled turbulent channel-porous media flow based upon neural networks, arxiv:2311.15600, 2023
[3] Intrusive versus non-intrusive reduced-order modeling of generalized Newtonian fluid flows, arxiv:2608.18259, 2026
