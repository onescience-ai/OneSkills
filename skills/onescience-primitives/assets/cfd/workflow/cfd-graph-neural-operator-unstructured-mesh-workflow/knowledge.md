# 图神经算子任意域非结构网格流场预测工作流

## 适用范围

本工作流卡为图神经算子（Graph Neural Operator）或MeshGraphNet在任意几何域非结构网格CFD数据上的流场预测提供端到端执行框架，覆盖5个核心步骤：数据接入与契约核验 → 预处理与数据切分 → 模型配置与训练 → 批量推理与物理恢复 → 任务验收与适用域判定。

## 工作流节点

```
s01 数据接入与契约核验
    ↓
s02 预处理与数据切分
    ↓
s03 模型配置与训练
    ↓
s04 批量推理与物理恢复
    ↓
s05 任务验收与适用域判定
```

## 节点详细说明

### s01 数据接入与契约核验

**操作**：读取非结构网格CFD数据集，建立数据清单，核验网格拓扑、变量定义、单位坐标、时间或工况范围、缺失值和使用许可。

**关键输入**：
- DATASET_PATH：数据集路径（必填）
- DATASET_NAME：数据集名称（必填，默认"任意几何非结构网格CFD数据"）
- DATA_CONTRACT：数据契约（可选，包含变量、单位、坐标定义）

**输出**：dataset_manifest.json, data_contract.json, data_audit.md

**质量门禁**：
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏

---

### s02 预处理与数据切分

**操作**：构建图结构（节点特征、边特征、邻接关系），按几何或工况切分数据集，执行归一化或无量纲化处理。

**关键输入**：
- SPLIT_CONFIG：切分配置（默认train:0.7, validation:0.15, test:0.15, seed:42, group_by:geometry_or_trajectory）
- TARGET_FIELDS：目标变量列表
- NONDIMENSIONALIZE：是否无量纲化（默认true）

**输出**：train_manifest.json, validation_manifest.json, test_manifest.json, normalization.json

**质量门禁**：
- 三份切分的对象轨迹互斥
- 仅用训练集计算变换统计量
- 图结构构建正确（节点数=网格单元数）

---

### s03 模型配置与训练

**操作**：配置Graph Neural Operator或MeshGraphNet模型，执行消息传递训练，保存最佳检查点。

**关键输入**：
- MODEL_NAME：模型名称（默认Graph Neural Operator、MeshGraphNet）
- TRAIN_CONFIG：训练配置（默认framework:PyTorch, epochs:100, batch_size:8, lr:0.001, seed:42, early_stopping_patience:15）
- INIT_CHECKPOINT：可选预训练权重

**输出**：best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt

**质量门禁**：
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

---

### s04 批量推理与物理恢复

**操作**：加载模型权重在独立测试集上推理，反归一化恢复物理单位、坐标网格、边界掩膜及任务派生量。

**关键输入**：
- CHECKPOINT：模型权重（默认best_checkpoint.pt）
- DEVICE：计算设备（默认cuda）
- BATCH_SIZE：推理批大小（默认8）

**输出**：predictions/, inference_manifest.json, timing.csv

**质量门禁**：
- 预测无NaN或Inf且形状单位正确
- 每个测试样本有唯一结果
- 推理未使用测试目标校正

---

### s05 任务验收与适用域判定

**操作**：按验收指标评价s04结果，至少报告逐变量误差、边界误差、守恒或方程残差、最差样本和推理成本。执行几何或工况外推测试并明确适用域。

**关键输入**：
- METRICS：验收指标（默认relative_L2, RMSE, conservation_residual, boundary_error）
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
- 若模型为多尺度版本（MultiScale MeshGraphNet），训练配置需调整为多分辨率参数
- 若推理发散，需检查图构建质量和模型兼容性
- 若外推测试失败，需在适用域报告中明确标注域外边界

## 资源召回建议

当需要执行完整的图神经算子非结构网格流场预测工作流时召回本卡。配合各步骤级任务卡（cfd-graph-neural-operator-unstructured-mesh-prediction）和场景卡（cfd-graph-neural-operator-arbitrary-domain-unstructured-mesh-flow-scenario）使用可获得详细执行指南。

## 证据来源
[1] Pfaff et al., "Learning Mesh-Based Simulation with Graph Networks", ICLR 2021, arXiv:2010.03409
[2] Fortunato et al., "MultiScale MeshGraphNets", ICML 2022 Workshop, arXiv:2210.00612
[3] Zhang et al., "Data-driven modeling of shock physics by physics-informed MeshGraphNets", arXiv:2602.14918, 2026