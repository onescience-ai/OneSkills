# 等变球面与Clifford神经算子学习（CFD_S057）

## 任务描述

面向球面向量场与三维对称PDE数据完成等变球面与Clifford神经算子学习。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流

### 步骤 1：数据接入与契约核验

**目的**：接入球面向量场与三维对称PDE数据，核验样本、变量、单位、网格坐标及许可。

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 数据集路径 | `{DATASET_PATH}` | doc | 是 | — | 目录或清单文件 |
| 数据集名称 | `{DATASET_NAME}` | str | 是 | `球面向量场与三维对称PDE数据` | 来源与数据版本 |
| 数据契约 | `{DATA_CONTRACT}` | object | 否 | {"input_fields": [], "target_fields": [], "units": {}, "coordinates": "dataset_native"} | 变量单位网格定义 |

**输出**：dataset_manifest.json、data_contract.json、data_audit.md

**质量门禁**：
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏

**操作指令**：`读取{DATASET_PATH}中的{DATASET_NAME}，为“等变球面与Clifford神经算子学习”建立数据清单。检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可，按{DATA_CONTRACT}输出机器可读契约。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

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

**目的**：训练Equivariant Neural Operator、Spherical FNO、Clifford Neural Operator完成指定输入到目标物理量的映射。

**依赖步骤**：s02

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 模型名称 | `{MODEL_NAME}` | str | 是 | `Equivariant Neural Operator、Spherical FNO、Clifford Neural Operator` | 实现或模型注册名 |
| 训练配置 | `{TRAIN_CONFIG}` | object | 是 | {"framework": "PyTorch", "epochs": 100, "batch_size": 8, "learning_rate": 0.001, "seed": 42, "early_stopping_patience": 15} | 超参数和随机种子 |
| 初始权重 | `{INIT_CHECKPOINT}` | doc | 否 | — | 可选预训练权重 |

**输出**：best_checkpoint.pt、train_config.json、training_metrics.csv、environment.txt

**质量门禁**：
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

**操作指令**：`使用{MODEL_NAME}，默认Equivariant Neural Operator、Spherical FNO、Clifford Neural Operator，和{TRAIN_CONFIG}训练“等变球面与Clifford神经算子学习”模型。加载s02切分与统计量，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。若提供{INIT_CHECKPOINT}须检查结构兼容性。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

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

1. **Group Equivariant Fourier Neural Operators for Partial Differential Equations** — sha256:80cec37e3dd4cbc510f62b4fdeeedd67102c859cfc489670570e80e5a225b05c
2. **DeltaPhi_ Physical States Residual Learning for Neural Operators in Data-Limited PDE Solving** — [sha256:7b641ca8d267e853b3e5f72fb0a6a1f391c14fdc0c708c6a74d23377a105bb85](https://arxiv.org/abs/2406.09795)
3. **Accelerating Data Generation for Neural Operators via Krylov Subspace Recycling** — sha256:0973bcc230357b5527367d23b9f18d5b41fbbac051cbe27ea3f20782c26ed0f8
4. **Equivariant Graph Neural Operator for Modeling 3D Dynamics** — sha256:bb77d94d5c0a72081cb461231540512e304d8e4e4fabe7718e0adb08ac2b2801
5. **Guaranteed Approximation Bounds for Mixed-Precision Neural Operators** — sha256:b8950a6a69db70d2cc8626e402d53af496ed93265a978d8015c3eb1e81090a5e
6. **An Intrinsic Vector Heat Network** — sha256:fae17c327fc23118733ecec2998d84802eab6e5ccf8ea482c88cd7b168c58056
7. **Random Grid Neural Processes for Parametric Partial Differential Equations** — sha256:9794108cf0e078ef8bde7d6c07f9d12ef02ba5a1c817bdca306dc597d2be994d
8. **Globally injective and bijective neural operators** — [sha256:7989f9db0461eaac16fef5be64c60c3aecd518c72341cf692968206e1e2d585d](https://arxiv.org/abs/2205.14627)
9. **Spherical Fourier Neural Operators_ Learning Stable Dynamics on the Sphere** — sha256:821fef0bd176dff6b988268acca52047cd741f94854ce774cb5e8348223ed0f7
10. **Can neural operators always be continuously discretized** — [sha256:f4c8a442803a63a49a8ba09d09ee671099fe94e23f33b4715ce5d359db440652](https://arxiv.org/abs/2205.14627)
11. **Banach neural operator for Navier–Stokes equations** — [sha256:aede5a5489bb6bc2d38a1f788d47ca9ca7cd2b5db8c2e9e8ae57a7a0c2ce79fd](https://arxiv.org/abs/2512.09070)
12. **Fengbo_ a Clifford Neural Operator pipeline for 3D PDEs in Computational Fluid Dynamics** — [sha256:a16fa0e1043991efe6b22e117c7122ecb09721c7bca50ad9c231ff647e7ba254](https://arxiv.org/abs/2209.04934)
13. **Generalized Spherical Neural Operators_ Green’s Function Formulation** — [sha256:b40007af40f8ecf674e8dee87ccd2dea36f687cad75da38e0771365d639aa56a](https://arxiv.org/abs/2104.13478)
14. **Locally Subspace-Informed Neural Operators for Efficient Multiscale PDE Solving** — [sha256:b51f7423f5da647a22f8d3ee82c0380f39ff9f5a22223d85194dc11c279c6dee](https://arxiv.org/abs/2509.12896)
