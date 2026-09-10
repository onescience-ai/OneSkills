# 工程LES等效源项与高保真校准（CFD_S080）

## 任务描述

面向叶轮高升力与工程LES及DNS数据完成工程LES等效源项与高保真校准。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流

### 步骤 1：数据接入与契约核验

**目的**：接入叶轮高升力与工程LES及DNS数据，核验样本、变量、单位、网格坐标及许可。

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 数据集路径 | `{DATASET_PATH}` | doc | 是 | — | 目录或清单文件 |
| 数据集名称 | `{DATASET_NAME}` | str | 是 | `叶轮高升力与工程LES及DNS数据` | 来源与数据版本 |
| 数据契约 | `{DATA_CONTRACT}` | object | 否 | {"input_fields": [], "target_fields": [], "units": {}, "coordinates": "dataset_native"} | 变量单位网格定义 |

**输出**：dataset_manifest.json、data_contract.json、data_audit.md

**质量门禁**：
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏

**操作指令**：`读取{DATASET_PATH}中的{DATASET_NAME}，为“工程LES等效源项与高保真校准”建立数据清单。检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可，按{DATA_CONTRACT}输出机器可读契约。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

### 步骤 2：预处理与数据切分

**目的**：统一物理量与表示，按几何、工况或时间构造无泄漏切分。

**依赖步骤**：s01

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 切分配置 | `{SPLIT_CONFIG}` | object | 是 | {"train": 0.7, "validation": 0.15, "test": 0.15, "seed": 42, "group_by": "geometry_or_trajectory"} | 按对象工况切分 |
| 目标变量 | `{TARGET_FIELDS}` | list[str] | 是 | ["按data_contract.json填写"] | 待预测物理量 |
| 是否无量纲化 | `{NONDIMENSIONALIZE}` | bool | 否 | true | 统一跨工况量纲 |

**输出**：train_manifest.json、validation_manifest.json、test_manifest.json、normalization.json

**质量门禁**：
- 三份切分的对象轨迹互斥
- 仅用训练集计算变换统计量
- 边界与掩膜语义未破坏

**操作指令**：`依据s01契约完成质控、重采样或图构建、掩膜、归一化或无量纲化。按{SPLIT_CONFIG}以几何、完整轨迹或物理工况为单位切分，不得把同一轨迹的帧随机打散。为{TARGET_FIELDS}保存统计量与可逆变换。`

### 步骤 3：模型配置与训练

**目的**：训练Data-driven LES source model完成指定输入到目标物理量的映射。

**依赖步骤**：s02

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 模型名称 | `{MODEL_NAME}` | str | 是 | `Data-driven LES source model` | 实现或模型注册名 |
| 训练配置 | `{TRAIN_CONFIG}` | object | 是 | {"framework": "PyTorch", "epochs": 100, "batch_size": 8, "learning_rate": 0.001, "seed": 42, "early_stopping_patience": 15} | 超参数和随机种子 |
| 初始权重 | `{INIT_CHECKPOINT}` | doc | 否 | — | 可选预训练权重 |

**输出**：best_checkpoint.pt、train_config.json、training_metrics.csv、environment.txt

**质量门禁**：
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

**操作指令**：`使用{MODEL_NAME}，默认Data-driven LES source model，和{TRAIN_CONFIG}训练“工程LES等效源项与高保真校准”模型。加载s02切分与统计量，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。若提供{INIT_CHECKPOINT}须检查结构兼容性。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

### 步骤 4：闭合项预测与后验CFD耦合

**目的**：先验评估闭合项，再嵌入RANS或LES执行稳定后验推进。

**依赖步骤**：s03

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 模型权重 | `{CHECKPOINT}` | doc | 是 | `best_checkpoint.pt` | 通过训练门限权重 |
| 计算设备 | `{DEVICE}` | str | 是 | `cuda` | CPU或CUDA设备 |
| 推理批大小 | `{BATCH_SIZE}` | int | 否 | `8` | 按显存调整批量 |

**输出**：apriori_closure/、aposteriori_fields/、solver_stability.csv

**质量门禁**：
- 闭合张量或通量满足约束
- 后验求解无非物理解和发散
- 均值剖面与能谱均经验证

**操作指令**：`加载{CHECKPOINT}预测应力、通量或源项，先在独立快照上做先验误差和可实现性检查，再嵌入对应RANS或LES求解器执行后验推进。保存残差、能谱、统计剖面与稳定性记录。`

### 步骤 5：任务验收与适用域判定

**目的**：评估统计误差、关键物理约束、泛化能力和计算收益。

**依赖步骤**：s04

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 验收指标 | `{METRICS}` | list[str] | 是 | ["closure_RMSE", "mean_profile_error", "spectrum_error", "stability_horizon"] | 统计和物理指标 |
| 相对误差门限 | `{MAX_RELATIVE_L2}` | float | 否 | `0.1` | 测试集放行阈值 |
| 是否外推测试 | `{RUN_OOD_TEST}` | bool | 否 | true | 测试域外工况 |

**输出**：evaluation.json、worst_cases.csv、applicability_report.md、PASS_REJECT_BLOCKED.txt

**质量门禁**：
- 统计与物理指标同时报告
- 最差样本可追溯
- 结论含适用域限制与复核建议

**操作指令**：`按{METRICS}评价s04结果，至少报告逐变量误差、边界误差、守恒或方程残差、最差样本和推理成本。使用{MAX_RELATIVE_L2}及任务物理门限给出PASS、REJECT或BLOCKED。若{RUN_OOD_TEST}为true，执行几何或工况外推测试并明确适用域，不得仅凭平均误差宣称工程可用。`

## 关联文献

1. **Data-driven impeller model for efficient large eddy simulations of metastable von Kármán flows** — [sha256:5c494606e1a30548b2017f93dcbc96f267be72a3a8e6a2b9620c57b5ff1e9a26](https://arxiv.org/abs/2607.25048)
2. **Deep learning observables in computational fluid dynamics** — [sha256:73fae85b2b9f30b6f8322397535ecb1993b0807ad490b1c89259761368d2fb7f](https://arxiv.org/abs/1903.03040)
3. **Learning to Estimate and Refine Fluid Motion with Physical Dynamics** — sha256:6bf7fe7b6da054874323b63a73a82ce83cd0d45d19c0983260107029daa81005
4. **Bayesian optimization and topographic exploration of drag-reducing dimples for aerodynamic surfaces** — [sha256:9c7a49fbc5a2155d6cc540be2f5c6b1f5355fc894ab5a00115e3b4f70b6f20fe](https://arxiv.org/abs/2608.12826)
5. **HiLiftAeroML_ High-Fidelity Computational Fluid Dynamics Dataset for High-Lift Aircraft Aerodynamics** — [sha256:bd87638212505fadd5a95b7a9d8e838ebd3621f5a3a51921b0392ca92b8cd590](https://arxiv.org/abs/2605.19565)
