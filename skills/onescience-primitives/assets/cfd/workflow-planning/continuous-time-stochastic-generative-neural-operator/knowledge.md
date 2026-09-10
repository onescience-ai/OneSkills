# 连续时间与随机生成神经算子预测（CFD_S060）

## 任务描述

面向随机或连续时间PDE分布数据完成连续时间与随机生成神经算子预测。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流

### 步骤 1：数据接入与契约核验

**目的**：接入随机或连续时间PDE分布数据，核验样本、变量、单位、网格坐标及许可。

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 数据集路径 | `{DATASET_PATH}` | doc | 是 | — | 目录或清单文件 |
| 数据集名称 | `{DATASET_NAME}` | str | 是 | `随机或连续时间PDE分布数据` | 来源与数据版本 |
| 数据契约 | `{DATA_CONTRACT}` | object | 否 | {"input_fields": [], "target_fields": [], "units": {}, "coordinates": "dataset_native"} | 变量单位网格定义 |

**输出**：dataset_manifest.json、data_contract.json、data_audit.md

**质量门禁**：
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏

**操作指令**：`读取{DATASET_PATH}中的{DATASET_NAME}，为“连续时间与随机生成神经算子预测”建立数据清单。检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可，按{DATA_CONTRACT}输出机器可读契约。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

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

**目的**：训练Continuous-time neural operator、Stochastic neural operator完成指定输入到目标物理量的映射。

**依赖步骤**：s02

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 模型名称 | `{MODEL_NAME}` | str | 是 | `Continuous-time neural operator、Stochastic neural operator` | 实现或模型注册名 |
| 训练配置 | `{TRAIN_CONFIG}` | object | 是 | {"framework": "PyTorch", "epochs": 100, "batch_size": 8, "learning_rate": 0.001, "seed": 42, "early_stopping_patience": 15} | 超参数和随机种子 |
| 初始权重 | `{INIT_CHECKPOINT}` | doc | 否 | — | 可选预训练权重 |

**输出**：best_checkpoint.pt、train_config.json、training_metrics.csv、environment.txt

**质量门禁**：
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

**操作指令**：`使用{MODEL_NAME}，默认Continuous-time neural operator、Stochastic neural operator，和{TRAIN_CONFIG}训练“连续时间与随机生成神经算子预测”模型。加载s02切分与统计量，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。若提供{INIT_CHECKPOINT}须检查结构兼容性。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

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

1. **CFO_ Learning Continuous-Time PDE Dynamics via Flow-Matched Neural Operators** — [sha256:a9c3a414f7315d3c0225047263ca728f72ce195d1435b3b3807cd8e056bbfb6f](https://arxiv.org/abs/2303.08797)
2. **Wavelet Diffusion Neural Operator** — sha256:a42dfa77130915c3e14c7d86a129a76b6b71448509d5146b5d4773682a927b5c
3. **Learning Semilinear Neural Operators_ A Unified Recursive Framework for Prediction and Data Assimilation** — sha256:f66fcd9c19c59b9856e8b93fcb739a8a7028162a29332c3118879740e739db87
4. **Boosting Generalization in Parametric PDE Neural Solvers through Adaptive Conditioning** — sha256:d0774672064545a0d3ef3bbab83433aa2e2635118ebda4cf6cddcdfa85155b6c
5. **Convolutional Neural Operators for Robust and Accurate Learning of PDEs** — sha256:ed6a05e8a95d94b960ebe49c57ad9498fe9a9facc7feab3a25885ee6588a6b5a
6. **Deep Equilibrium Based Neural Operators for Steady-State PDEs** — sha256:83518e6ae2ec33c4194035e2c7ca34767fd654e6e82ac13fa2193415d732e4c1
7. **Representation Equivalent Neural Operators_ a Framework for Alias-free Operator Learning** — sha256:30b1ea448fe719d5844ea40fdfcb2e56deb2dc3574daefe979bca635df701f4a
8. **Neural Stochastic PDEs_ Resolution-Invariant Learning of Continuous Spatiotemporal Dynamics** — sha256:66ddb1e2298b45546bb779bab0fe7f49dc4e7c2fd1a1bcd05e7495101cb6e44e
9. **Variational Autoencoding Neural Operators** — sha256:f7d23ad05ab49eb8d7d5bed21743901a27aeba58520e7cd668a958e8449814c6
10. **Newton Informed Neural Operator for Solving Nonlinear Partial Differential Equations** — [sha256:b953a2b638515f9058e10ee3cd8fb76fd386abac9e5fb946f7145b1697102032](https://arxiv.org/abs/2207.05748)
11. **Linearization Turns Neural Operators into Function-Valued Gaussian Processes** — sha256:f5b5577e66ca31ee86dee9edf2084542f4d0e3ce5898c7c220b402525c54a755
12. **Optimization for Neural Operators can Benefit from Width** — sha256:0327d40b252ad58868f7a1fd044a0835165f27cbf8f9341b1e751f25fa40557a
13. **KANO_ Kolmogorov-Arnold Neural Operator** — [sha256:6f5b6327b7a6d57af72e5833824db5597d0506d7775840394b9dc794bc9d2d61](https://arxiv.org/abs/2406.14495)
14. **Riesz Neural Operator for Solving Partial Differential Equations** — sha256:d0837cf0c1dc841d69119b28d90bc02c7c8ba1fa3d0a0d489929bd316693e5d5
