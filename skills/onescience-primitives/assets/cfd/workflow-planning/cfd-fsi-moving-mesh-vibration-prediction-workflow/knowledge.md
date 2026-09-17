# 流固耦合移动网格振动时序预测工作流

## 适用范围
流固耦合（FSI）移动网格振动时序预测的端到端工作流，覆盖从数据接入到验收的完整闭环。适用于采用ALE（任意拉格朗日-欧拉）神经网络或图模拟器（Graph Simulator）对涡激振动与流固耦合轨迹数据进行训练和预测的任务。

## 输入
- 数据集路径（{DATASET_PATH}）
- 数据集名称（{DATASET_NAME}）
- 数据契约（{DATA_CONTRACT}，可选）
- 切分配置（{SPLIT_CONFIG}）
- 目标变量列表（{TARGET_FIELDS}）
- 模型名称（{MODEL_NAME}，默认ALE neural network、Graph simulator）
- 训练配置（{TRAIN_CONFIG}）
- 初始权重（{INIT_CHECKPOINT}，可选）
- 计算设备（{DEVICE}）
- 验收指标（{METRICS}）

## 输出
- 数据集清单（dataset_manifest.json）
- 数据契约（data_contract.json）
- 数据审计报告（data_audit.md）
- 三份切分清单（train/validation/test_manifest.json）
- 归一化统计量（normalization.json）
- 最佳模型权重（best_checkpoint.pt）
- 训练配置与指标（train_config.json, training_metrics.csv）
- 环境信息（environment.txt）
- 推理结果（predictions/）
- 推理清单与耗时（inference_manifest.json, timing.csv）
- 评估报告（evaluation.json, worst_cases.csv, applicability_report.md）
- 验收结论（PASS_REJECT_BLOCKED.txt）

## 流程节点
```
s01 数据接入与契约核验
  │  输入：{DATASET_PATH}, {DATASET_NAME}, {DATA_CONTRACT}
  │  输出：dataset_manifest.json, data_contract.json, data_audit.md
  │  质量门禁：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏
  ▼
s02 预处理与数据切分
  │  输入：{SPLIT_CONFIG}, {TARGET_FIELDS}, {NONDIMENSIONALIZE}
  │  输出：train/validation/test_manifest.json, normalization.json
  │  质量门禁：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏
  ▼
s03 模型配置与训练
  │  输入：{MODEL_NAME}, {TRAIN_CONFIG}, {INIT_CHECKPOINT}
  │  输出：best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt
  │  质量门禁：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现
  ▼
s04 批量推理与物理恢复
  │  输入：{CHECKPOINT}, {DEVICE}, {BATCH_SIZE}
  │  输出：predictions/, inference_manifest.json, timing.csv
  │  质量门禁：预测无NaN或Inf且形状单位正确；每个测试样本有唯一结果；推理未使用测试目标校正
  ▼
s05 任务验收与适用域判定
     输入：{METRICS}, {MAX_RELATIVE_L2}, {RUN_OOD_TEST}
     输出：evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt
     质量门禁：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议
```

## 关键参数

### 通用判据
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 切分方式 | 按几何或完整轨迹为单位 | 场景需求书s02 | 不得把同一轨迹的帧随机打散 |
| 验收指标 | relative_L2, RMSE, conservation_residual, boundary_error | 场景需求书s05 | 统计与物理指标必须同时报告 |
| 外推测试 | 需要（默认true） | 场景需求书s05 | 几何或工况外推测试决定适用域边界 |

### 校准数值
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| train/val/test比例 | 0.7/0.15/0.15 | 场景需求书s02 | 以下数值来自场景默认配置，其他体系需以自身证据重新锚定 |
| 随机种子 | 42 | 场景需求书 | |
| 相对误差门限 | 0.1 | 场景需求书s05 | |

## 边界与分流
- s01 缺少必填输入时返回BLOCKED并列出缺项
- s02 切分配置无效时回退到默认比例（0.7/0.15/0.15）
- s03 训练损失为NaN/Inf时REJECT并检查数据或模型配置
- s04 推理失败时检查checkpoint兼容性和设备可用性
- s05 未通过验收时输出REJECT并附详细原因，域外工况需CFD复核

## 质量检查
- 每步有独立质量门禁，未通过则阻断后续步骤
- 全流程随机种子可复现
- 所有中间产物可追溯

## 回退策略
- 任一步骤BLOCKED/REJECT时，定位具体缺项或失败原因后重试
- 模型训练不收敛时调整超参数或检查数据质量
- 推理阶段OOM时降低batch_size

## 资源召回建议
- 本卡片为工作流级卡片，可被以下需求召回：FSI振动预测流程、流固耦合时序预测工作流、ALE/Graph模型CFD工作流
- 配套场景卡片：cfd-fsi-moving-mesh-vibration-time-series-prediction
- 配套任务卡片：各步骤独立任务卡片

## 证据来源
[1] Neural Latent Arbitrary Lagrangian-Eulerian Grids for Fluid-Solid Interaction
[2] Deep learning of vortex-induced vibrations, arXiv:1808.08952, 2018
