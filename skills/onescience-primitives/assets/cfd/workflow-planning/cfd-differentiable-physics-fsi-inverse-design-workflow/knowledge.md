# 可微物理流固耦合逆向设计工作流

## 适用范围
可微物理流固耦合逆向设计的端到端工作流，覆盖从数据接入到验收的完整闭环。适用于采用可微物理（Differentiable Physics）或图模拟器（Graph Simulator）模型，从流固耦合轨迹数据中学习物理规律，并通过逆向优化生成满足目标性能的设计方案的任务。

## 输入
- 数据集路径（{DATASET_PATH}）
- 数据集名称（{DATASET_NAME}）
- 数据契约（{DATA_CONTRACT}，可选）
- 切分配置（{SPLIT_CONFIG}）
- 目标变量列表（{TARGET_FIELDS}）
- 模型名称（{MODEL_NAME}，默认Differentiable physics、Graph simulator）
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
- 设计候选（design_candidates/）
- 优化历史（optimization_history.csv）
- Pareto前沿（pareto_front.json）
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
s04 候选生成与约束优化
  │  输入：{CHECKPOINT}, {DEVICE}, {BATCH_SIZE}
  │  输出：design_candidates/, optimization_history.csv, pareto_front.json
  │  质量门禁：候选满足几何和物理硬约束；优化轨迹与随机种子完整；最优候选未混用测试标签
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
| 切分方式 | 按几何、完整轨迹或物理工况为单位 | 场景需求书s02 | 不得把同一轨迹的帧随机打散 |
| 验收指标 | objective_improvement, constraint_violation, CFD_validation_error | 场景需求书s05 | 统计与物理指标必须同时报告 |
| 外推测试 | 需要（默认true） | 场景需求书s05 | 几何或工况外推测试决定适用域边界 |
| 逆向优化 | 需要保留完整搜索轨迹 | 场景需求书s04 | 不得把代理预测直接当作高保真认证结果 |

### 校准数值
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| train/val/test比例 | 0.7/0.15/0.15 | 场景需求书s02 | 以下数值来自场景默认配置，其他体系需以自身证据重新锚定 |
| 随机种子 | 42 | 场景需求书 | |
| 相对误差门限 | 0.1 | 场景需求书s05 | |
| 训练轮次 | 100 | 场景需求书s03 | |
| 批大小 | 8 | 场景需求书s03/s04 | |
| 学习率 | 0.001 | 场景需求书s03 | |

## 边界与分流
- s01 缺少必填输入时返回BLOCKED并列出缺项
- s02 切分配置无效时回退到默认比例（0.7/0.15/0.15）
- s03 训练损失为NaN/Inf时REJECT并检查数据或模型配置
- s04 候选不满足几何和物理硬约束时重新生成
- s05 未通过验收时输出REJECT并附详细原因，域外工况需CFD复核

## 质量检查
- 每步有独立质量门禁，未通过则阻断后续步骤
- 全流程随机种子可复现
- 所有中间产物可追溯
- 候选生成与优化需保留完整搜索轨迹
- 物理一致性评估需包含守恒性验证

## 回退策略
- 任一步骤BLOCKED/REJECT时，定位具体缺项或失败原因后重试
- 模型训练不收敛时调整超参数或检查数据质量
- 优化搜索失败时调整约束条件或搜索策略
- 适用域判定不通过时扩大训练数据范围或简化模型

## 资源召回建议
- 本卡片为工作流级卡片，可被以下需求召回：可微物理逆向设计工作流、FSI逆向设计流程、Differentiable physics inverse design workflow
- 配套场景卡片：cfd-differentiable-physics-fsi-inverse-design-scenario
- 配套任务卡片：各步骤独立任务卡片

## 证据来源
[1] PRDP_ Progressively Refined Differentiable Physics
[2] PETAL_ Physics Emulation Through Averaged Linearizations for Solving Inverse Problems