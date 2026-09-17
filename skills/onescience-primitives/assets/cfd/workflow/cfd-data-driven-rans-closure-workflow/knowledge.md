# 数据驱动RANS湍流闭合工作流

## 适用范围

本工作流卡为数据驱动RANS湍流闭合提供端到端执行框架，覆盖5个核心步骤：数据接入与契约核验 → 预处理与数据切分 → 模型配置与训练 → 闭合项预测与后验CFD耦合 → 任务验收与适用域判定。

## 工作流节点

```
s01 数据接入与契约核验
    ↓
s02 预处理与数据切分
    ↓
s03 模型配置与训练
    ↓
s04 闭合项预测与后验CFD耦合
    ↓
s05 任务验收与适用域判定
```

## 节点详细说明

### s01 数据接入与契约核验

**操作**：读取DNS与RANS配对湍流闭合数据集，建立数据清单，核验文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可。

**关键输入**：
- DATASET_PATH：数据集路径（必填）
- DATASET_NAME：数据集名称（必填，默认"DNS与RANS配对湍流闭合数据"）
- DATA_CONTRACT：数据契约（可选，包含变量、单位、坐标定义）

**输出**：dataset_manifest.json, data_contract.json, data_audit.md

**质量门禁**：
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏

---

### s02 预处理与数据切分

**操作**：依据s01契约完成质控、重采样或图构建、掩膜、归一化或无量纲化。按配置以几何、完整轨迹或物理工况为单位切分。

**关键输入**：
- SPLIT_CONFIG：切分配置（默认train:0.7, validation:0.15, test:0.15, seed:42, group_by:geometry_or_trajectory）
- TARGET_FIELDS：目标变量列表
- NONDIMENSIONALIZE：是否无量纲化（默认true）

**输出**：train_manifest.json, validation_manifest.json, test_manifest.json, normalization.json

**质量门禁**：
- 三份切分的对象轨迹互斥
- 仅用训练集计算变换统计量
- 边界与掩膜语义未破坏

---

### s03 模型配置与训练

**操作**：加载切分与统计量，使用指定模型（Tensor-basis neural network或Symbolic closure model）完成从输入到目标物理量的映射训练。记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。

**关键输入**：
- MODEL_NAME：模型名称（默认Tensor-basis neural network、Symbolic closure model）
- TRAIN_CONFIG：训练配置（默认framework:PyTorch, epochs:100, batch_size:8, lr:0.001, seed:42, early_stopping_patience:15）
- INIT_CHECKPOINT：可选预训练权重

**输出**：best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt

**质量门禁**：
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

---

### s04 闭合项预测与后验CFD耦合

**操作**：加载模型权重预测应力、通量或源项。先在独立快照上做先验误差和可实现性检查，再嵌入对应RANS或LES求解器执行后验推进。保存残差、能谱、统计剖面与稳定性记录。

**关键输入**：
- CHECKPOINT：模型权重（默认best_checkpoint.pt）
- DEVICE：计算设备（默认cuda）
- BATCH_SIZE：推理批大小（默认8）

**输出**：apriori_closure/, aposteriori_fields/, solver_stability.csv

**质量门禁**：
- 闭合张量或通量满足约束
- 后验求解无非物理解和发散
- 均值剖面与能谱均经验证

---

### s05 任务验收与适用域判定

**操作**：按验收指标评价s04结果，至少报告逐变量误差、边界误差、守恒或方程残差、最差样本和推理成本。执行几何或工况外推测试并明确适用域。

**关键输入**：
- METRICS：验收指标（默认closure_RMSE, mean_profile_error, spectrum_error, stability_horizon）
- MAX_RELATIVE_L2：相对误差门限（默认0.1）
- RUN_OOD_TEST：是否外推测试（默认true）

**输出**：evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt

**质量门禁**：
- 统计与物理指标同时报告
- 最差样本可追溯
- 结论含适用域限制与复核建议

## 关键参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| train/val/test split | 0.7/0.15/0.15 | 切分比例 |
| random seed | 42 | 可复现性种子 |
| framework | PyTorch | 训练框架 |
| epochs | 100 | 最大训练轮数 |
| batch_size | 8 | 批大小 |
| learning_rate | 0.001 | 学习率 |
| early_stopping_patience | 15 | 早停耐心值 |
| MAX_RELATIVE_L2 | 0.1 | 相对误差门限 |

## 边界与分流

- 若数据集为单工况无切分需求，可跳过几何切分直接按时间切分
- 若模型为符号回归模型（Symbolic closure model），训练配置需调整为符号搜索参数
- 若后验推进发散，需检查闭合项可实现性并降低学习率重训
- 若外推测试失败，需在适用域报告中明确标注域外边界

## 资源召回建议

当需要执行完整的数据驱动湍流闭合工作流时召回本卡。配合各步骤级任务卡（cfd-data-ingestion-contract-validation, cfd-preprocessing-data-splitting, cfd-model-config-training, cfd-closure-prediction-coupling, cfd-acceptance-applicability）使用可获得详细执行指南。