# 物理网络随机与高维PDE求解（CFD_S046）

## 任务描述

面向随机微分方程与高维PDE样本完成物理网络随机与高维PDE求解。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流

### 步骤 1：数据接入与契约核验

**目的**：接入随机微分方程与高维PDE样本，核验样本、变量、单位、网格坐标及许可。

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 数据集路径 | `{DATASET_PATH}` | doc | 是 | — | 目录或清单文件 |
| 数据集名称 | `{DATASET_NAME}` | str | 是 | `随机微分方程与高维PDE样本` | 来源与数据版本 |
| 数据契约 | `{DATA_CONTRACT}` | object | 否 | {"input_fields": [], "target_fields": [], "units": {}, "coordinates": "dataset_native"} | 变量单位网格定义 |

**输出**：dataset_manifest.json、data_contract.json、data_audit.md

**质量门禁**：
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏

**操作指令**：`读取{DATASET_PATH}中的{DATASET_NAME}，为“物理网络随机与高维PDE求解”建立数据清单。检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可，按{DATA_CONTRACT}输出机器可读契约。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

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

**目的**：训练Physics-informed stochastic solver、Gaussian process完成指定输入到目标物理量的映射。

**依赖步骤**：s02

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 模型名称 | `{MODEL_NAME}` | str | 是 | `Physics-informed stochastic solver、Gaussian process` | 实现或模型注册名 |
| 训练配置 | `{TRAIN_CONFIG}` | object | 是 | {"framework": "PyTorch", "epochs": 100, "batch_size": 8, "learning_rate": 0.001, "seed": 42, "early_stopping_patience": 15} | 超参数和随机种子 |
| 初始权重 | `{INIT_CHECKPOINT}` | doc | 否 | — | 可选预训练权重 |

**输出**：best_checkpoint.pt、train_config.json、training_metrics.csv、environment.txt

**质量门禁**：
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

**操作指令**：`使用{MODEL_NAME}，默认Physics-informed stochastic solver、Gaussian process，和{TRAIN_CONFIG}训练“物理网络随机与高维PDE求解”模型。加载s02切分与统计量，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。若提供{INIT_CHECKPOINT}须检查结构兼容性。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

### 步骤 4：方程求解与物理残差恢复

**目的**：在查询配点或网格上恢复解场、导数、边界值与方程残差。

**依赖步骤**：s03

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 模型权重 | `{CHECKPOINT}` | doc | 是 | `best_checkpoint.pt` | 通过训练门限权重 |
| 计算设备 | `{DEVICE}` | str | 是 | `cuda` | CPU或CUDA设备 |
| 推理批大小 | `{BATCH_SIZE}` | int | 否 | `8` | 按显存调整批量 |

**输出**：solution_fields/、pde_residuals/、boundary_residuals.csv

**质量门禁**：
- 解场导数与残差均为有限值
- 边初值逐项满足门限
- 独立数值解或解析解可对照

**操作指令**：`加载{CHECKPOINT}，在测试参数、边界和查询坐标上求解目标PDE，使用自动微分或离散算子恢复导数、通量和方程残差。保存解场与残差场；禁止只依据训练损失判定方程已求解。`

### 步骤 5：任务验收与适用域判定

**目的**：评估统计误差、关键物理约束、泛化能力和计算收益。

**依赖步骤**：s04

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 验收指标 | `{METRICS}` | list[str] | 是 | ["relative_L2", "PDE_residual", "boundary_error", "conservation_error"] | 统计和物理指标 |
| 相对误差门限 | `{MAX_RELATIVE_L2}` | float | 否 | `0.1` | 测试集放行阈值 |
| 是否外推测试 | `{RUN_OOD_TEST}` | bool | 否 | true | 测试域外工况 |

**输出**：evaluation.json、worst_cases.csv、applicability_report.md、PASS_REJECT_BLOCKED.txt

**质量门禁**：
- 统计与物理指标同时报告
- 最差样本可追溯
- 结论含适用域限制与复核建议

**操作指令**：`按{METRICS}评价s04结果，至少报告逐变量误差、边界误差、守恒或方程残差、最差样本和推理成本。使用{MAX_RELATIVE_L2}及任务物理门限给出PASS、REJECT或BLOCKED。若{RUN_OOD_TEST}为true，执行几何或工况外推测试并明确适用域，不得仅凭平均误差宣称工程可用。`

## 关联文献

1. **Aerodynamic force reconstruction using physics-informed Gaussian processes** — [sha256:f912ec0f95daf9629977a8b0460acc5f23f1bfbe5615d76787e6e4ec999f5077](https://arxiv.org/abs/2605.22111)
2. **Integration Matters for Learning PDEs with Backward SDEs** — [sha256:4dae5e1768c19bd5cfb9a44fd5abd5c51e7597ded5428670b4c14858d2553cb9](https://arxiv.org/abs/2505.01078)
3. **PIG_ Physics-Informed Gaussians as Adaptive Parametric Mesh Representations** — sha256:ea150502f8d515136a359ad71945b91f2fb14474ad853fb3c495dc8a84b90bc3
4. **Score-based free-form architectures for high-dimensional Fokker-Planck equations** — sha256:c183a7368aed3dc88a2b8c70299594775bd893dafb73690e25a4dd556b2e3059
5. **In-Context Learning of Stochastic Differential Equations with Foundation Inference Models** — [sha256:af18f6bd50e9150c5c31f64fbb93f7bacd948b493fbc8193cb556bb580776c38](https://arxiv.org/abs/2502.19049)
6. **Learning in modal space_ Solving time-dependent stochastic PDEs using physics-informed neural networks** — [sha256:8d4568c110b3c99f303c7efe84d56b1e9006671cba8b6402c83e6fb62594759b](https://arxiv.org/abs/1905.01205)
7. **Gaussian Process Priors for Systems of Linear Partial Differential Equations with Constant Coefficients** — sha256:17dd59203237ba5963ca67afa1f191d47c16a2ab669ff47b91caafaa74a4a9e5
8. **Physics-informed machine learning with smoothed particle hydrodynamics_ Hierarchy of reduced Lagrangian mode** — [sha256:88320b4b918c6456712d92a8bbd1e16f0c77ca419e311fa1248ac667cccc9123](https://doi.org/10.1103/PhysRevFluids.8.054602)
9. **Learning a Neural Solver for Parametric PDEs to Enhance Physics-Informed Methods** — [sha256:0d5f1e439b72bec352245722a2faba5f3463f2f2a3ca8d9ab097c0deb0ee22a4](https://doi.org/10.1145/3620665.3640366)
10. **Physics-Informed Inference Time Scaling for Solving High-Dimensional Partial Differential Equations** — sha256:67cfcc205ea4312be9cd5c7d91d938055c3c3ccdb2d707ba8fd8fb5db82b862c
11. **UrbanGraph_ Physics-Informed Spatio-Temporal Dynamic Heterogeneous Graphs for Urban Microclimate Prediction** — [sha256:142b25c80d82927db2e04d3be017f1297151e6e88fa9e5f18f61626d69d6258f](https://doi.org/10.1016/j.buildenv)
12. **Physics-Informed Kolmogorov-Arnold networks for viscoelastic fluid equations** — [sha256:2e395e01afb657c056ca0491bdf0d928fc8488331417bf9065107d7b99224930](https://arxiv.org/abs/2608.29895)
