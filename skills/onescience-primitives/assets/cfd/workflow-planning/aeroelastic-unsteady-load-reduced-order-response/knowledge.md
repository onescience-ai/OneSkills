# 气动弹性与非定常载荷降阶响应预测（CFD_S089）

## 任务描述

面向非定常气动力与耦合响应时序完成气动弹性与非定常载荷降阶响应预测。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流

### 步骤 1：数据接入与契约核验

**目的**：接入非定常气动力与耦合响应时序，核验样本、变量、单位、网格坐标及许可。

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 数据集路径 | `{DATASET_PATH}` | doc | 是 | — | 目录或清单文件 |
| 数据集名称 | `{DATASET_NAME}` | str | 是 | `非定常气动力与耦合响应时序` | 来源与数据版本 |
| 数据契约 | `{DATA_CONTRACT}` | object | 否 | {"input_fields": [], "target_fields": [], "units": {}, "coordinates": "dataset_native"} | 变量单位网格定义 |

**输出**：dataset_manifest.json、data_contract.json、data_audit.md

**质量门禁**：
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏

**操作指令**：`读取{DATASET_PATH}中的{DATASET_NAME}，为“气动弹性与非定常载荷降阶响应预测”建立数据清单。检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可，按{DATA_CONTRACT}输出机器可读契约。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

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

**目的**：训练Neural aerodynamic ROM、Neural ODE完成指定输入到目标物理量的映射。

**依赖步骤**：s02

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 模型名称 | `{MODEL_NAME}` | str | 是 | `Neural aerodynamic ROM、Neural ODE` | 实现或模型注册名 |
| 训练配置 | `{TRAIN_CONFIG}` | object | 是 | {"framework": "PyTorch", "epochs": 100, "batch_size": 8, "learning_rate": 0.001, "seed": 42, "early_stopping_patience": 15} | 超参数和随机种子 |
| 初始权重 | `{INIT_CHECKPOINT}` | doc | 否 | — | 可选预训练权重 |

**输出**：best_checkpoint.pt、train_config.json、training_metrics.csv、environment.txt

**质量门禁**：
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

**操作指令**：`使用{MODEL_NAME}，默认Neural aerodynamic ROM、Neural ODE，和{TRAIN_CONFIG}训练“气动弹性与非定常载荷降阶响应预测”模型。加载s02切分与统计量，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。若提供{INIT_CHECKPOINT}须检查结构兼容性。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

### 步骤 4：批量推理与物理恢复

**目的**：在独立测试集推理，恢复原始单位、网格和物理派生量。

**依赖步骤**：s03

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 模型权重 | `{CHECKPOINT}` | doc | 是 | `best_checkpoint.pt` | 通过训练门限权重 |
| 计算设备 | `{DEVICE}` | str | 是 | `cuda` | CPU或CUDA设备 |
| 推理批大小 | `{BATCH_SIZE}` | int | 否 | `8` | 按显存调整批量 |

**输出**：predictions/、inference_manifest.json、timing.csv

**质量门禁**：
- 预测无NaN或Inf且形状单位正确
- 每个测试样本有唯一结果
- 推理未使用测试目标校正

**操作指令**：`加载{CHECKPOINT}及训练时数据契约，在s02独立测试集上以{DEVICE}和{BATCH_SIZE}推理。反归一化并恢复物理单位、坐标网格、边界掩膜及任务派生量，保存逐样本结果和耗时，禁止用测试标签修正预测。`

### 步骤 5：任务验收与适用域判定

**目的**：评估统计误差、关键物理约束、泛化能力和计算收益。

**依赖步骤**：s04

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 验收指标 | `{METRICS}` | list[str] | 是 | ["relative_L2", "RMSE", "conservation_residual", "boundary_error"] | 统计和物理指标 |
| 相对误差门限 | `{MAX_RELATIVE_L2}` | float | 否 | `0.1` | 测试集放行阈值 |
| 是否外推测试 | `{RUN_OOD_TEST}` | bool | 否 | true | 测试域外工况 |

**输出**：evaluation.json、worst_cases.csv、applicability_report.md、PASS_REJECT_BLOCKED.txt

**质量门禁**：
- 统计与物理指标同时报告
- 最差样本可追溯
- 结论含适用域限制与复核建议

**操作指令**：`按{METRICS}评价s04结果，至少报告逐变量误差、边界误差、守恒或方程残差、最差样本和推理成本。使用{MAX_RELATIVE_L2}及任务物理门限给出PASS、REJECT或BLOCKED。若{RUN_OOD_TEST}为true，执行几何或工况外推测试并明确适用域，不得仅凭平均误差宣称工程可用。`

## 关联文献

1. **Modeling Unsteady Aircraft Aerodynamics Using Lorenz Attractor_ A Reduced-Order Approach for Wing Rock** — sha256:70dc850b91c5c4cf7f992bbdf51cb04925daa5bc854d6e670ea8cac0e7203085
2. **Deep Learning-Based Reduced Order Model for Three-Dimensional Unsteady Flow Using Mesh Transformation and Stitching** — sha256:f0e0e03d47d2a80086de90a5645f7a40e081f66608eb4f37718d9a5ab3184c16
3. **Stable Port-Hamiltonian Neural Networks** — [sha256:bb2b6c594a2560b578899a7958fbef6a59a6fad85a97144bc86307e1b794f5fb](https://arxiv.org/abs/2502.02480)
4. **Convolutional neural network and long short-term memory based reduced order surrogate for minimal turbulent chan** — [sha256:67e0a251ab022814fba33de4c3328bcabc27be0f6d8af31b6bd704a0d1c98995](https://arxiv.org/abs/2010.13351)
5. **A deep learning enabler for nonintrusive reduced order modeling of fluid flows** — [sha256:0b9925bed11004ca4b92b6658a7c4d3630f9908f4ff113d5323450746171bd1e](https://arxiv.org/abs/1907.04945)
6. **Validation and parameterization of a novel physics-constrained neural dynamics model applied to turbulent fl** — [sha256:c488dfcde1a46821b77d4589810e657d23eb5de9cac5589c9c8d8d1967c2110c](https://arxiv.org/abs/2110.11528)
7. **Amortized Inference for Model Rocket Aerodynamics _ Learning to Estimate Physical Parameters from Simulation** — [sha256:1804c04948160b58f9fcc1f365779298586b38fe25010e074e9131fb3d2942de](https://arxiv.org/abs/2512.22248)
8. **A Residual Learning Approach for Unsteady Aerodynamic Load Prediction** — [sha256:5016e827777365fbed651adcc8cbd30047caaa71a126102c985cf5fea20a22fd](https://arxiv.org/abs/2608.17894)
9. **Kolmogorov Arnold networks (KAN) for aerodynamic prediction_ a comparison with MLPs and GNNs** — [sha256:4608d166f210ec3b3a8768938f7e2fffe76126f7dd5a0fe524becdd36a78eaba](https://arxiv.org/abs/2606.27126)
10. **Neural-Network and Reduced-order Modeling Workflows for AI-Driven CFD_ Fast Response Surfaces, Reduced Dynamics and Jet in Cross-flow Examples** — [sha256:55cd20efe6d7f15fc907954cf9cd366311d2e55acc7b46ce521eeaac13625cf7](https://arxiv.org/abs/2608.26064)
11. **Nonlinear Model Order Reduction for Coupled Aeroelastic-Flight Dynamic Systems** — [sha256:13fca741f8df32ecd497caa19a0bd00b83c05113237a79c9bcec37c631206074](https://arxiv.org/abs/2603.15296)
