# FNO规则网格参数化PDE算子学习（CFD_S048）

## 任务描述

面向Darcy与Navier-Stokes规则网格数据完成FNO规则网格参数化PDE算子学习。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流

### 步骤 1：数据接入与契约核验

**目的**：接入Darcy与Navier-Stokes规则网格数据，核验样本、变量、单位、网格坐标及许可。

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 数据集路径 | `{DATASET_PATH}` | doc | 是 | — | 目录或清单文件 |
| 数据集名称 | `{DATASET_NAME}` | str | 是 | `Darcy与Navier-Stokes规则网格数据` | 来源与数据版本 |
| 数据契约 | `{DATA_CONTRACT}` | object | 否 | {"input_fields": [], "target_fields": [], "units": {}, "coordinates": "dataset_native"} | 变量单位网格定义 |

**输出**：dataset_manifest.json、data_contract.json、data_audit.md

**质量门禁**：
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏

**操作指令**：`读取{DATASET_PATH}中的{DATASET_NAME}，为“FNO规则网格参数化PDE算子学习”建立数据清单。检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可，按{DATA_CONTRACT}输出机器可读契约。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

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

**目的**：训练Fourier Neural Operator完成指定输入到目标物理量的映射。

**依赖步骤**：s02

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 模型名称 | `{MODEL_NAME}` | str | 是 | `Fourier Neural Operator` | 实现或模型注册名 |
| 训练配置 | `{TRAIN_CONFIG}` | object | 是 | {"framework": "PyTorch", "epochs": 100, "batch_size": 8, "learning_rate": 0.001, "seed": 42, "early_stopping_patience": 15} | 超参数和随机种子 |
| 初始权重 | `{INIT_CHECKPOINT}` | doc | 否 | — | 可选预训练权重 |

**输出**：best_checkpoint.pt、train_config.json、training_metrics.csv、environment.txt

**质量门禁**：
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

**操作指令**：`使用{MODEL_NAME}，默认Fourier Neural Operator，和{TRAIN_CONFIG}训练“FNO规则网格参数化PDE算子学习”模型。加载s02切分与统计量，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。若提供{INIT_CHECKPOINT}须检查结构兼容性。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

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

1. **Tucker-FNO_ Tensor Tucker-Fourier Neural Operator and its Universal Approximation Theory** — sha256:b6cc6bc0766552c036dbbde470ef427775c1d5648232008f5b1ef86be3366e03
2. **Fourier Neural Operator for Parametric Partial Differential Equations** — [sha256:6cd2645d4a50d1a61a261529b33747c674d78851bdbe6993b0961f81a17dc6f2](https://arxiv.org/abs/2010.08895)
3. **Factorized Fourier Neural Operators** — [sha256:3c2b0d0ea005c031417e32d1659cfc0ad71898927b71a8218572d99169b3aee8](https://arxiv.org/abs/2111.13802)
4. **Maximal Update Parametrization and Zero-Shot Hyperparameter Transfer for Fourier Neural Operators** — sha256:63af33b452ba0eacb241ff70d87f30923dbbd8d9ba616f09ae0d48d4825fe753
5. **Sensitivity-Constrained Fourier Neural Operators for Forward and Inverse Problems in Parametric Differential Equations** — sha256:86a63eb8517e37ff6662f68801beedfa2d0bc51a1c6502f6528b3359193054b1
6. **Beyond Regular Grids_ Fourier-Based Neural Operators on Arbitrary Domains** — sha256:8cf365ae93e7215616815556371ddc46c812cb3475280e53384371f1f5bcff3c
7. **Domain Agnostic Fourier Neural Operators** — sha256:15ff729c7a902f1049166b32763c052c32c157f2f2fe6bb12741558bfbf396f8
8. **U-FNO_ An Enhanced Fourier Neural Operator-Based Deep-Learning Model for Multiphase Flow** — [sha256:3ac2875f51a30b644213275ad380a929415ef85401049d889e22c7131869755e](https://arxiv.org/abs/2109.03697)
9. **Understanding the Expressivity and Trainability of Fourier Neural Operator_ A Mean-Field Perspective** — [sha256:7531aeed4df008ae7cd5eddaa0b74c0913b05f388b42adf64c7f0e0c7cf0dc6b](https://arxiv.org/abs/2111.13587)
10. **Spectral-Refiner_ Accurate Fine-Tuning of Spatiotemporal Fourier Neural Operator for Turbulent Flows** — sha256:225a98abd2481bdc75b9ed075173a88383d190ce252cd7e773ec43e0e4cc3794
11. **Extending Fourier Neural Operators for Modeling Parameterized and Coupled PDEs** — [sha256:24b234b94baa4ac8cd3e1bc159a9c46d2b5d4a971c3bfdf293c2f8aea3a7cae3](https://arxiv.org/abs/2505.24717)
12. **Evaluation of State-of-the-Art Deep Learning Architectures for Aerodynamical Predictions** — [sha256:9764585ef34a6cb07c94921df9974b411fbb9f8eb0d24f534838b831435bcdca](https://arxiv.org/abs/2607.13866)
