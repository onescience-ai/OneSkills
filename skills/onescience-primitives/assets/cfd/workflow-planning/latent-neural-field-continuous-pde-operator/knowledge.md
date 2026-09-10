# 潜空间与神经场连续PDE算子学习（CFD_S054）

## 任务描述

面向连续坐标与压缩潜空间PDE数据完成潜空间与神经场连续PDE算子学习。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流

### 步骤 1：数据接入与契约核验

**目的**：接入连续坐标与压缩潜空间PDE数据，核验样本、变量、单位、网格坐标及许可。

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 数据集路径 | `{DATASET_PATH}` | doc | 是 | — | 目录或清单文件 |
| 数据集名称 | `{DATASET_NAME}` | str | 是 | `连续坐标与压缩潜空间PDE数据` | 来源与数据版本 |
| 数据契约 | `{DATA_CONTRACT}` | object | 否 | {"input_fields": [], "target_fields": [], "units": {}, "coordinates": "dataset_native"} | 变量单位网格定义 |

**输出**：dataset_manifest.json、data_contract.json、data_audit.md

**质量门禁**：
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏

**操作指令**：`读取{DATASET_PATH}中的{DATASET_NAME}，为“潜空间与神经场连续PDE算子学习”建立数据清单。检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可，按{DATA_CONTRACT}输出机器可读契约。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

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

**目的**：训练Latent Neural Operator、Neural field operator完成指定输入到目标物理量的映射。

**依赖步骤**：s02

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 模型名称 | `{MODEL_NAME}` | str | 是 | `Latent Neural Operator、Neural field operator` | 实现或模型注册名 |
| 训练配置 | `{TRAIN_CONFIG}` | object | 是 | {"framework": "PyTorch", "epochs": 100, "batch_size": 8, "learning_rate": 0.001, "seed": 42, "early_stopping_patience": 15} | 超参数和随机种子 |
| 初始权重 | `{INIT_CHECKPOINT}` | doc | 否 | — | 可选预训练权重 |

**输出**：best_checkpoint.pt、train_config.json、training_metrics.csv、environment.txt

**质量门禁**：
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

**操作指令**：`使用{MODEL_NAME}，默认Latent Neural Operator、Neural field operator，和{TRAIN_CONFIG}训练“潜空间与神经场连续PDE算子学习”模型。加载s02切分与统计量，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。若提供{INIT_CHECKPOINT}须检查结构兼容性。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

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

1. **Latent Neural Operator for Solving Forward and Inverse PDE Problems** — sha256:efc0c7a38403538d8d9c3a4474c0ba517f3f04125c5d7c1e1108827ce7c70a18
2. **Discretization-invariance_ On the Discretization Mismatch Errors in Neural Operators** — sha256:3181bece3c23193322a28ea9cbbc88c815babd000cf48003e4e52c419b047c07
3. **Neural Emulator Superiority_ When Machine Learning for PDEs Surpasses its Training Data** — [sha256:067586949389579707516a1e4130c254fdd9b2416f1633b4fd7dc048d255f2d2](https://arxiv.org/abs/2510.23111)
4. **Implicit Representations via Operator Learning** — sha256:a4b1e5c261efd22bb30d03be1d111d9d115614c5eebc6828f3050e21501ef0ec
5. **Neural operators meet conjugate gradients_ The FCG-NO method for efficient PDE solving** — sha256:0792ebf4dc128e9315e50d05b3cbfb12a6beb257f0d30d8a4716ef5e2b45a66e
6. **GNOT_ A General Neural Operator Transformer for Operator Learning** — sha256:0610b9455ecb6cb1276d2eee08596265317be260353e0e23d2b847da38067e58
7. **General Covariance Data Augmentation for Neural PDE Solvers** — sha256:20b5b1db9a95267d1cb4e7f7f5d4991729f6bbbd3063a5516b557261cccf1bb9
8. **Operator Learning with Neural Fields_ Tackling PDEs on General Geometries** — sha256:cf12e24eab059075330843924d88053b3c556b7a9a410564fe56ad33e4f8f081
9. **Solving High-Dimensional PDEs with Latent Spectral Models** — sha256:d2edbe315f74d67007a58e2d19e695efeac64ddb433b7e99ab3bf09dd01e55e7
10. **Meta-Auto-Decoder for Solving Parametric Partial Differential Equations** — sha256:bc12bcf70cbadae14f62f1323b5dd192881190a46f845ea37cbbbaf65fd5646f
11. **A Bregman Proximal Viewpoint on Neural Operators** — sha256:4c707f6bc6ceaab9a09c765c2ece88ce54588745cc6cf170df40a498e2da3ef9
12. **GridMix_ Exploring Spatial Modulation for Neural Fields in PDE Modeling** — [sha256:6df06620eaf40e42d619b12efc6e7e693c94bcb9a6c2fd9268f274348a7b0aa1](https://arxiv.org/abs/2302.03130)
13. **Quantitative Approximation for Neural Operators in Nonlinear Parabolic Equations** — sha256:cce46f8994fe7323fd2b0589e2a0cf68d6027173652aea35e28ea6931ffbeff6
14. **Disentangled Representation Learning for Parametric Partial Differential Equations** — sha256:1c50547c061e74e4107c526315e8d807c225a0c8e2f0a5827199749648fe8aea
15. **Accelerating Bayesian inverse design in computational fluid dynamics using neural operators** — [sha256:f271ce5f230b72fb485a0e58937ce63893fb95440282f507feaebaabda894a55](https://arxiv.org/abs/2605.26059)
