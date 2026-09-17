# 稀疏观测PINN湍流闭合联合反演工作流

## 适用范围

覆盖从稀疏实验观测数据接入到最终适用域判定的完整工作流，适用于利用Physics-Informed Neural Networks (PINN)联合反演RANS均值流场与湍流闭合项的全过程。每步含明确的输入输出契约与质量门禁。

## 输入

- 稀疏实验观测数据集（路径、名称、数据契约）
- RANS方程约束
- 计算几何信息与工况参数

## 输出

- 5步产物：数据清单/契约、切分清单、训练权重与指标、闭合预测与后验场、验收报告与适用域判定

## 流程节点

```
s01 数据接入与契约核验
  → s02 预处理与数据切分
    → s03 模型配置与训练
      → s04 闭合项预测与后验CFD耦合
        → s05 任务验收与适用域判定
```

### s01 数据接入与契约核验

**操作**：接入稀疏实验观测与RANS方程数据，核验样本、变量、单位、网格坐标及许可。检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可，按数据契约输出机器可读契约。

**参数**：{DATASET_PATH}（目录或清单文件）、{DATASET_NAME}（来源与数据版本）、{DATA_CONTRACT}（变量单位网格定义）

**工具**：文件读取、JSON/CSV解析

**质量门禁**：
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏

**产出**：dataset_manifest.json, data_contract.json, data_audit.md

### s02 预处理与数据切分

**操作**：依据s01契约完成质控、重采样或图构建、掩膜、归一化或无量纲化。按{SPLIT_CONFIG}以几何、完整轨迹或物理工况为单位切分，不得把同一轨迹的帧随机打散。为{TARGET_FIELDS}保存统计量与可逆变换。

**参数**：{SPLIT_CONFIG}（train:0.7, val:0.15, test:0.15, seed:42, group_by:geometry_or_trajectory）、{TARGET_FIELDS}（待预测物理量）、{NONDIMENSIONALIZE}（是否无量纲化）

**工具**：数值计算库、数据切分工具

**质量门禁**：
- 三份切分的对象轨迹互斥
- 仅用训练集计算变换统计量
- 边界与掩膜语义未破坏

**产出**：train_manifest.json, validation_manifest.json, test_manifest.json, normalization.json

### s03 模型配置与训练

**操作**：使用Turbulence PINN，加载s02切分与统计量，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。若提供{INIT_CHECKPOINT}须检查结构兼容性。

**参数**：{MODEL_NAME}（默认Turbulence PINN）、{TRAIN_CONFIG}（framework:PyTorch, epochs:100, batch_size:8, learning_rate:0.001, seed:42, early_stopping_patience:15）、{INIT_CHECKPOINT}（可选预训练权重）

**工具**：PyTorch、训练循环

**质量门禁**：
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

**产出**：best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt

### s04 闭合项预测与后验CFD耦合

**操作**：加载{CHECKPOINT}预测应力、通量或源项，先在独立快照上做先验误差和可实现性检查，再嵌入对应RANS或LES求解器执行后验推进。保存残差、能谱、统计剖面与稳定性记录。

**参数**：{CHECKPOINT}（通过训练门限权重）、{DEVICE}（CPU或CUDA）、{BATCH_SIZE}（按显存调整，默认8）

**工具**：PINN推理引擎、RANS/LES求解器

**质量门禁**：
- 闭合张量或通量满足约束
- 后验求解无非物理解和发散
- 均值剖面与能谱均经验证

**产出**：apriori_closure/, aposteriori_fields/, solver_stability.csv

### s05 任务验收与适用域判定

**操作**：按{METRICS}评价s04结果，至少报告逐变量误差、边界误差、守恒或方程残差、最差样本和推理成本。使用{MAX_RELATIVE_L2}及任务物理门限给出PASS、REJECT或BLOCKED。若{RUN_OOD_TEST}为true，执行几何或工况外推测试并明确适用域。

**参数**：{METRICS}（closure_RMSE, mean_profile_error, spectrum_error, stability_horizon）、{MAX_RELATIVE_L2}（默认0.1）、{RUN_OOD_TEST}（默认true）

**工具**：误差分析、物理约束验证

**质量门禁**：
- 统计与物理指标同时报告
- 最差样本可追溯
- 结论含适用域限制与复核建议

**产出**：evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 训练框架 | PyTorch | [场景需求书] | 默认实现框架 |
| 训练轮数 | 100 | [场景需求书] | 可根据收敛调整 |
| 批大小 | 8 | [场景需求书] | 按显存调整 |
| 学习率 | 0.001 | [场景需求书] | 基线超参数 |
| 早停耐心 | 15 | [场景需求书] | 防止过拟合 |
| 切分比例 | 0.7/0.15/0.15 | [场景需求书] | train/val/test |
| 切分种子 | 42 | [场景需求书] | 可复现性 |
| 切分依据 | geometry_or_trajectory | [场景需求书] | 按对象或轨迹分组 |
| 误差门限 | 0.1 | [场景需求书] | 相对L2范数 |

## 边界与分流

- s01缺少必填输入 → 返回BLOCKED，不得编造
- s02数据切分违反轨迹互斥 → 报错并要求重新切分
- s03训练发散 → 检查物理约束权重与学习率
- s04后验求解发散 → 检查闭合项可实现性，必要时施加物理裁剪
- s05域外测试失败 → 标注适用域边界，建议CFD复核

## 质量检查

- 每步均有独立质量门禁，通过后方可进入下一步
- 最差样本必须可追溯至具体工况与位置
- 最终判定必须包含PASS/REJECT/BLOCKED明确结论

## 回退策略

- 数据不足：返回BLOCKED，补充数据后重试
- 训练失败：调整超参数或简化网络架构
- 后验耦合失败：降级为纯先验评估
- 适用域不明：扩大测试范围或标记待验证

## 资源召回建议

当需要执行完整的稀疏观测PINN湍流闭合反演流程时召回本卡片。各步骤可独立召回对应的task级卡片（cfd-sparse-data-intake-contract-verification、cfd-pinn-preprocessing-data-split、cfd-turbulence-pinn-model-training、cfd-pinn-closure-aposteriori-coupling、cfd-pinn-closure-validation-applicability）。

## 证据来源

[1] Turbulence Closure in RANS and Flow Inference around a Cylinder using PINNs and Sparse Experimental Data, arXiv:2510.06049, 2025
[2] Turbulence closure in Reynolds-averaged Navier–Stokes and flow inference around a cylinder using physics-informed neural networks, J. Fluid Mech., 2026, DOI: 10.1017/jfm.2026.11471
