# 物理边界与不变量约束神经算子学习（CFD_S059）

## 任务描述

面向带守恒边界和无量纲约束PDE数据完成物理边界与不变量约束神经算子学习。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流

### 步骤 1：数据接入与契约核验

**目的**：接入带守恒边界和无量纲约束PDE数据，核验样本、变量、单位、网格坐标及许可。

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 数据集路径 | `{DATASET_PATH}` | doc | 是 | — | 目录或清单文件 |
| 数据集名称 | `{DATASET_NAME}` | str | 是 | `带守恒边界和无量纲约束PDE数据` | 来源与数据版本 |
| 数据契约 | `{DATA_CONTRACT}` | object | 否 | {"input_fields": [], "target_fields": [], "units": {}, "coordinates": "dataset_native"} | 变量单位网格定义 |

**输出**：dataset_manifest.json、data_contract.json、data_audit.md

**质量门禁**：
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏

**操作指令**：`读取{DATASET_PATH}中的{DATASET_NAME}，为“物理边界与不变量约束神经算子学习”建立数据清单。检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可，按{DATA_CONTRACT}输出机器可读契约。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

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

**目的**：训练Physics-constrained neural operator完成指定输入到目标物理量的映射。

**依赖步骤**：s02

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 模型名称 | `{MODEL_NAME}` | str | 是 | `Physics-constrained neural operator` | 实现或模型注册名 |
| 训练配置 | `{TRAIN_CONFIG}` | object | 是 | {"framework": "PyTorch", "epochs": 100, "batch_size": 8, "learning_rate": 0.001, "seed": 42, "early_stopping_patience": 15} | 超参数和随机种子 |
| 初始权重 | `{INIT_CHECKPOINT}` | doc | 否 | — | 可选预训练权重 |

**输出**：best_checkpoint.pt、train_config.json、training_metrics.csv、environment.txt

**质量门禁**：
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

**操作指令**：`使用{MODEL_NAME}，默认Physics-constrained neural operator，和{TRAIN_CONFIG}训练“物理边界与不变量约束神经算子学习”模型。加载s02切分与统计量，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。若提供{INIT_CHECKPOINT}须检查结构兼容性。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

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

1. **Guiding Continuous Operator Learning through Physics-Based Boundary Constraints** — [sha256:6c62d031966b8b481906bed8d39865c018ea10600735cd3c6b8924dba64c895d](https://arxiv.org/abs/2212.07477)
2. **Holistic Physics Solver_ Learning PDEs in a Unified Spectral-Physical Space** — sha256:1b9ed40c90451ec4133370890aec33f9a7a754345f9d6eaeb04568a5703e6790
3. **Learn Singularly Perturbed Solutions via Homotopy Dynamics** — sha256:bcfb19e02bea0e446ddff6acda6170a536abc49ecc457c7994f25bb0cea8df53
4. **A Physics-preserved Transfer Learning Method for Differential Equations** — [sha256:32ec88a75d06a926cf10125274e7ffd55b062867fd405a604bc26efd2ad76896](https://arxiv.org/abs/2505.01281)
5. **Nonlocal Attention Operator_ Materializing Hidden Knowledge Towards Interpretable Physics Discovery** — sha256:057908770784033f21f4260b8f7ea8b1bd5c3d2a69c82b1fdb4c75e373709e83
6. **PAPM_ A Physics-aware Proxy Model for Process Systems** — sha256:e59913aea8e8df36adab5eae2473291287111c97bc2b820cb7059f9179b9ca3f
7. **Training neural operators to preserve invariant measures of chaotic attractors** — sha256:da6751e6b634d98407847d421de241788c8a9ba50f3c0e10a12e84fed929e182
8. **Generic bounds on the approximation error for physics-informed (and) operator learning** — sha256:52fdd5646f266544e611d73bc7bc2d8cfcb7c8ad10e85ed48e854e2db651992e
9. **Buckingham $_pi$-Invariant Test‐Time Projection for Robust PDE Surrogate Modeling** — [sha256:c6f9099e0dd1d07e07cd3d3b3b34ffd4313f4c668d8b34bfd2756c978c68d8b3](https://arxiv.org/abs/2410.03263)
10. **Towards Generalizable PDE Dynamics Forecasting via Physics-Guided Invariant Learning** — [sha256:ff60a10c9ea880d0cb38cb955396c80bfddc7b09b9059014b2ec361bc3935bc4](https://arxiv.org/abs/1907.02893)
11. **WAN3DNS_ Weak Adversarial Networks for Solving 3D Incompressible Navier-Stokes Equations** — [sha256:a31dcf027830936d2f2221a96ca4b85e95b8cd6c94371855f0c33d61f61bb4a8](https://arxiv.org/abs/2509.26034)
12. **Wrong-Physics Backdoors in Neural PDE Operators** — [sha256:785e859f67f7b0447e06f9b271c0f27e58732a31c268d05e48359d1c480faa5a](https://arxiv.org/abs/2608.20439)
