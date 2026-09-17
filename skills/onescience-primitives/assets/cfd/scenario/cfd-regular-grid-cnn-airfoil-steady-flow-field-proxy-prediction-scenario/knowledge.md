# 场景：CFD_S001 — 规则网格CNN翼型稳态流场代理预测

- domain: cfd
- type: paper_scenario
- scenario_id: CFD_S001

## 问题与适用性

面向DeepCFD规则网格翼型RANS数据完成规则网格CNN翼型稳态流场代理预测。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

**适用边界**：
- 适用：规则网格、翼型几何、稳态层流/湍流RANS数据、CNN/U-Net架构
- 不适用：非结构网格、三维复杂几何、非定常流、需要高精度湍流建模的场景
- 域外工况需经CFD复核

## 资源配置

| 类别 | 值 | 说明 |
|------|-----|------|
| 模型 | CNN, U-Net | 核心神经网络架构 |
| 工具 | （源场景未提供） | 待确认 |
| 算力 | NULL | 无特定HPC要求 |
| 数据集 | DeepCFD规则网格翼型RANS数据 | 输入数据来源 |

## 工作流概览

5步端到端工作流，经 edge:workflow 指向 `cnn-airfoil-steady-flow-surrogate`：

| 步骤 | 名称 | 依赖 | 核心输出 | 质量门禁要点 |
|------|------|------|----------|-------------|
| s01 | 数据接入与契约核验 | — | dataset_manifest.json, data_contract.json, data_audit.md | 数据可读、变量完整、无泄漏 |
| s02 | 预处理与数据切分 | s01 | train/val/test_manifest.json, normalization.json | 切分互斥、统计量仅训练集、边界语义完整 |
| s03 | 模型配置与训练 | s02 | best_checkpoint.pt, training_metrics.csv | 损失有限、权重可加载、可复现 |
| s04 | 批量推理与物理恢复 | s03 | predictions/, inference_manifest.json, timing.csv | 无NaN/Inf、形状正确、未用测试标签 |
| s05 | 任务验收与适用域判定 | s04 | evaluation.json, applicability_report.md, PASS_REJECT_BLOCKED.txt | 统计+物理指标、最差可追溯、含适用域限制 |

## 关键输入槽

| 槽位 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| DATASET_PATH | doc | 是 | — | 数据集路径 |
| DATASET_NAME | str | 是 | DeepCFD规则网格翼型RANS数据 | 数据集名称 |
| DATA_CONTRACT | object | 否 | {input_fields:[], target_fields:[], units:{}, coordinates:dataset_native} | 数据契约 |
| SPLIT_CONFIG | object | 是 | {train:0.7, val:0.15, test:0.15, seed:42, group_by:geometry_or_trajectory} | 切分配置 |
| TARGET_FIELDS | list[str] | 是 | [按data_contract.json填写] | 目标变量 |
| NONDIMENSIONALIZE | bool | 否 | true | 是否无量纲化 |
| MODEL_NAME | str | 是 | CNN、U-Net | 模型名称 |
| TRAIN_CONFIG | object | 是 | {framework:PyTorch, epochs:100, batch_size:8, lr:0.001, seed:42, early_stopping_patience:15} | 训练配置 |
| INIT_CHECKPOINT | doc | 否 | — | 可选预训练权重 |
| CHECKPOINT | doc | 是 | best_checkpoint.pt | 模型权重 |
| DEVICE | str | 是 | cuda | 计算设备 |
| BATCH_SIZE | int | 否 | 8 | 推理批大小 |
| METRICS | list[str] | 是 | [relative_L2, RMSE, conservation_residual, boundary_error] | 验收指标 |
| MAX_RELATIVE_L2 | float | 否 | 0.1 | 相对误差门限 |
| RUN_OOD_TEST | bool | 否 | true | 是否外推测试 |

## 关联论文

1. [1] DeepCFD: Efficient steady-state laminar flow approximation with deep convolutional neural networks — arXiv:2004.08826, 2020
2. [2] A composable machine-learning approach for steady-state simulations on high-resolution grids — （无DOI）
3. [3] A Hybrid CNN-Cheby-KAN Framework for Efficient Prediction of Two-Dimensional Airfoil Pressure Distribution — arXiv:2511.03223, 2025
4. [4] Towards Interpretable Damage Detection based on Aerodynamic Pressure Measurements — arXiv:2605.08187, 2026

## 验收与缺失信息策略

- acceptance_decision: （源场景未提供）
- missing_information_policy: （源场景未提供）

## 资源召回建议

- 需要召回本场景时：使用查询词包含 "airfoil"、"CNN"、"steady-state"、"surrogate"、"DeepCFD"、"规则网格"、"翼型"、"代理预测" 等
- 配套工作流卡：`cnn-airfoil-steady-flow-surrogate`
- 配套任务卡：5个骨架任务的实例化版本（见 edge:task 标签）
