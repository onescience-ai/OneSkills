# 潜空间神经ODE连续流动动力学预测（CFD_S019）

## 任务描述

面向连续时间PDE状态序列完成潜空间神经ODE连续流动动力学预测。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流

### 步骤 1：数据接入与契约核验

**目的**：接入连续时间PDE状态序列，核验样本、变量、单位、网格坐标及许可。

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 数据集路径 | `{DATASET_PATH}` | doc | 是 | — | 目录或清单文件 |
| 数据集名称 | `{DATASET_NAME}` | str | 是 | `连续时间PDE状态序列` | 来源与数据版本 |
| 数据契约 | `{DATA_CONTRACT}` | object | 否 | {"input_fields": [], "target_fields": [], "units": {}, "coordinates": "dataset_native"} | 变量单位网格定义 |

**输出**：dataset_manifest.json、data_contract.json、data_audit.md

**质量门禁**：
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏

**操作指令**：`读取{DATASET_PATH}中的{DATASET_NAME}，为“潜空间神经ODE连续流动动力学预测”建立数据清单。检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可，按{DATA_CONTRACT}输出机器可读契约。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

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

**目的**：训练Neural ODE、Latent neural field完成指定输入到目标物理量的映射。

**依赖步骤**：s02

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 模型名称 | `{MODEL_NAME}` | str | 是 | `Neural ODE、Latent neural field` | 实现或模型注册名 |
| 训练配置 | `{TRAIN_CONFIG}` | object | 是 | {"framework": "PyTorch", "epochs": 100, "batch_size": 8, "learning_rate": 0.001, "seed": 42, "early_stopping_patience": 15} | 超参数和随机种子 |
| 初始权重 | `{INIT_CHECKPOINT}` | doc | 否 | — | 可选预训练权重 |

**输出**：best_checkpoint.pt、train_config.json、training_metrics.csv、environment.txt

**质量门禁**：
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

**操作指令**：`使用{MODEL_NAME}，默认Neural ODE、Latent neural field，和{TRAIN_CONFIG}训练“潜空间神经ODE连续流动动力学预测”模型。加载s02切分与统计量，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。若提供{INIT_CHECKPOINT}须检查结构兼容性。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

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

1. **AROMA_ Preserving Spatial Structure for Latent PDE Modeling with Local Neural Fields** — sha256:cfda478477037ff650fdb0da90aba930f77f23b4c977fd559aca20bfc4207235
2. **CALM-PDE_ Continuous and Adaptive Convolutions for Latent Space Modeling of Time-dependent PDEs** — [sha256:1078afb81def22cec33e71a3bb92c12528dfbe54d502d7766bf0ec2f1de20990](https://arxiv.org/abs/2505.12944)
3. **Poisson-Dirac Neural Networks for Modeling Coupled Dynamical Systems across Domains** — sha256:efa2169a6dd7a04a427d1e219049612c25c7745a7e0a98f868002b7fcb48aec7
4. **Hierarchical Implicit Neural Emulators** — [sha256:a95fb94d633b1f284c08a4954f6874e7ba72501b304f7b07883e6dee067930e7](https://arxiv.org/abs/2506.04528)
5. **Zero-Shot Transfer of Neural ODEs** — sha256:e86f3fe3f7938f7a0f5bdf77729eea0a260b165ec1da3010d9e0722311da6a19
6. **ClimODE_ Climate and Weather Forecasting with Physics-informed Neural ODEs** — sha256:bdcdf4e0f1b61bbfe53982183f0bb0174c040284c3d4d2d3c38b1d3e15ca86f0
7. **Vectorized Conditional Neural Fields_ A Framework for Solving Time-dependent Parametric Partial Differential Equ** — sha256:d50a51dfbb34c83c823d2d16e60447baf6edcc6aef0e21738e5ad46e5356b474
8. **Implicit Neural Spatial Representations for Time-dependent PDEs** — sha256:056011736b781b5c9869aed771e7ef428619d7f5a24857a614487796a2478a2a
9. **Clifford Neural Layers for PDE Modeling** — [sha256:f29679968df9e17d0931e5d6580c003655cf68fb56b53fbabcfb68477a249471](https://arxiv.org/abs/2209.04934)
10. **Continuous PDE Dynamics Forecasting with Implicit Neural Representations** — [sha256:bec6426577a3c7dfdc68fc6aa90374be49c3b8669cc27e6cb394c5b33b8e24da](https://arxiv.org/abs/2209.14855)
11. **Latent Field Discovery in Interacting Dynamical Systems with Neural Fields** — sha256:f3fe7484970055a7f942ca689462d5d0a580d0464d3d4d4963cf9bb89e8d4731
12. **Modulated Neural ODEs** — sha256:025cae39b1c3a3c6d2481710486c3c57896148a1aac3ebe867760fcf71fb1e93
13. **Phase2vec_ dynamical systems embedding with a physics-informed convolutional network** — [sha256:335c89f95cbedcd9057e4b5aea1be02c10be7caab4706c377150948c0ae0226a](https://arxiv.org/abs/2212.03857)
14. **Learning to Accelerate Partial Differential Equations via Latent Global Evolution** — sha256:000fe97742a06d1e73b968af13a7de5f0cf3045b3b21c4d45de640644d7bbb63
