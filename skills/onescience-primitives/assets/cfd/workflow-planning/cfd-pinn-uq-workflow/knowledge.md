# 物理信息概率网络流场不确定性反演工作流

## 适用范围

本工作流适用于使用物理信息概率网络（Bayesian PINN、Physics-informed GAN）进行流场不确定性反演的完整流程。每步含明确的输入输出契约、质量门禁和依赖关系。

## 输入

- **稀疏观测数据集**：含传感器坐标与流场物理量
- **CFD先验信息**：控制方程、边界条件、初始条件
- **切分配置**：训练/验证/测试集比例、切分策略

## 输出

- **工作流产物**：
  - dataset_manifest.json / data_contract.json / data_audit.md
  - train/validation/test_manifest.json / normalization.json
  - best_checkpoint.pt / train_config.json / training_metrics.csv
  - predictive_distribution/ / uncertainty_decomposition.json / calibration.csv
  - evaluation.json / worst_cases.csv / applicability_report.md
  - PASS_REJECT_BLOCKED.txt

## 流程节点

```
s01 数据接入与契约核验
  ↓
s02 预处理与数据切分
  ↓
s03 模型配置与训练
  ↓
s04 概率推理与不确定性校准
  ↓
s05 任务验收与适用域判定
```

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 训练集比例 | 0.7 | 场景需求书 | 默认切分比例 |
| 验证集比例 | 0.15 | 场景需求书 | 默认切分比例 |
| 测试集比例 | 0.15 | 场景需求书 | 默认切分比例 |
| 随机种子 | 42 | 场景需求书 | 默认种子 |
| 切分策略 | geometry_or_trajectory | 场景需求书 | 按几何或轨迹切分 |
| 无量纲化 | true | 场景需求书 | 默认执行 |

## 边界与分流

- **s01 BLOCKED**：缺少必填输入（数据集路径、数据集名称）时返回BLOCKED
- **s02 数据泄漏**：同一轨迹的帧被打散时需重新切分
- **s03 不收敛**：训练验证损失非有限值时需调整配置
- **s04 失败**：测试集参与校准训练时需重做推理
- **s05 REJECT**：相对误差超过门限或物理约束不满足时拒绝

## 质量检查

| 步骤 | 质量门禁 |
|------|----------|
| s01 | 数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏 |
| s02 | 三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏 |
| s03 | 训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现 |
| s04 | 概率输出有限且定义清楚；测试集未参与校准训练；区间覆盖率与宽度同时报告 |
| s05 | 统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议 |

## 回退策略

- 数据质量差时，返回s01重新核验
- 切分不当导致泄漏时，返回s02调整切分策略
- 模型不收敛时，返回s03调整超参数
- 校准失败时，检查概率输出格式或调整校准方法

## 资源召回建议

当用户需要执行完整的PINN/UQ工作流时召回本卡片。各步骤卡片可单独召回用于特定阶段：
- cfd-data-ingestion-contract-validation（s01）
- cfd-preprocessing-split（s02）
- cfd-model-training-config（s03）
- cfd-probabilistic-inference-calibration（s04）
- cfd-acceptance-applicability（s05）

## 证据来源

基于场景需求书CFD_S016工作流定义提炼。
