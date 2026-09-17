# CFD Foundation Model Multiphysics Operator Transfer Workflow

## 适用范围

面向将预训练科学基础模型迁移到多物理场CFD预测任务的标准工作流，覆盖从数据接入到适用域判定的完整闭环。适用于 PDE foundation model 和 Pretrained neural operator 的迁移学习场景。

## 输入

- 预训练模型 checkpoint 或模型注册名
- 目标任务数据集路径
- 训练配置（超参数、随机种子）
- 验收指标与门限

## 输出

- 迁移后模型权重（best_checkpoint.pt）
- 任务结果预测场
- 评估报告（evaluation.json）
- 适用域报告（applicability_report.md）
- 复现制品（train_config.json、environment.txt、training_metrics.csv）

## 流程节点

```
s01: 数据接入与契约核验
  ├─ 输入: DATASET_PATH, DATASET_NAME, DATA_CONTRACT
  ├─ 操作: 检查文件可读性、样本数、变量单位、坐标系、网格拓扑、缺失值、使用许可
  ├─ 输出: dataset_manifest.json, data_contract.json, data_audit.md
  └─ 质量门禁: 数据文件可读且样本可追溯、输入目标变量单位坐标定义完整、不存在训练测试泄漏

s02: 预处理与数据切分 (依赖 s01)
  ├─ 输入: SPLIT_CONFIG, TARGET_FIELDS, NONDIMENSIONALIZE
  ├─ 操作: 统一物理量、归一化/无量纲化、按几何/轨迹/工况无泄漏切分
  ├─ 输出: train/validation/test_manifest.json, normalization.json
  └─ 质量门禁: 三份切分互斥、仅用训练集计算变换统计量、边界掩膜语义未破坏

s03: 模型配置与训练 (依赖 s02)
  ├─ 输入: MODEL_NAME, TRAIN_CONFIG, INIT_CHECKPOINT
  ├─ 操作: 加载预训练权重、fine-tune、记录训练验证指标
  ├─ 输出: best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt
  └─ 质量门禁: 训练验证损失有限、最佳权重可重新加载、配置环境随机种子可复现

s04: 批量推理与物理恢复 (依赖 s03)
  ├─ 输入: CHECKPOINT, DEVICE, BATCH_SIZE
  ├─ 操作: 独立测试集推理、反归一化、恢复物理单位网格、保存逐样本结果
  ├─ 输出: predictions/, inference_manifest.json, timing.csv
  └─ 质量门禁: 预测无NaN/Inf、每个样本有唯一结果、推理未使用测试目标校正

s05: 任务验收与适用域判定 (依赖 s04)
  ├─ 输入: METRICS, MAX_RELATIVE_L2, RUN_OOD_TEST
  ├─ 操作: 统计误差+物理约束+泛化能力评估、外推测试、适用域确定
  ├─ 输出: evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt
  └─ 质量门禁: 统计物理指标同时报告、最差样本可追溯、结论含适用域限制与复核建议
```

## 关键参数

| 参数 | 默认值 | 来源 | 说明 |
|------|--------|------|------|
| train_ratio | 0.7 | 场景需求书 | 训练集占比 |
| validation_ratio | 0.15 | 场景需求书 | 验证集占比 |
| test_ratio | 0.15 | 场景需求书 | 测试集占比 |
| epochs | 100 | 场景需求书 | 最大训练轮次 |
| batch_size | 8 | 场景需求书 | 批大小 |
| learning_rate | 0.001 | 场景需求书 | 学习率 |
| seed | 42 | 场景需求书 | 随机种子 |
| early_stopping_patience | 15 | 场景需求书 | 早停耐心 |
| MAX_RELATIVE_L2 | 0.1 | 场景需求书 | 相对L2误差门限 |

## 边界与分流

- 步骤间依赖严格顺序，s01 失败则全链路 BLOCKED
- s03 权重加载失败 → 检查 checkpoint 结构兼容性或转向从头训练
- s05 PASS 以外结果 → 根据 REJECT/BLOCKED 原因决定是否回退调整

## 质量检查

每个步骤完成后检查对应 quality_gate，全部通过才进入下一步骤。

## 回退策略

- 数据质量问题 → 返回 s01 重新核验
- 训练不收敛 → 调整超参后从 s03 重试
- 物理约束违反 → 调整 loss 权重后从 s03 重试

## 资源召回建议

当需要执行完整的多物理算子迁移工作流时召回本卡片。

配套任务卡：
- cfd-foundation-model-data-intake-contract-validation
- cfd-foundation-model-preprocessing-data-splitting
- cfd-foundation-model-training
- cfd-foundation-model-inference-physical-recovery
- cfd-foundation-model-acceptance-applicability

## 证据来源

[1] 场景需求书 CFD_S056 workflow 定义
