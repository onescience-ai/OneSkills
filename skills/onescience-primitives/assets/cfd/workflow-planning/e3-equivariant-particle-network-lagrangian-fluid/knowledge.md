# E3等变粒子网络拉格朗日流体模拟（CFD_S062）

## 任务描述

面向拉格朗日粒子轨迹数据完成E3等变粒子网络拉格朗日流体模拟。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流

### 步骤 1：数据接入与契约核验

**目的**：接入拉格朗日粒子轨迹数据，核验样本、变量、单位、网格坐标及许可。

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 数据集路径 | `{DATASET_PATH}` | doc | 是 | — | 目录或清单文件 |
| 数据集名称 | `{DATASET_NAME}` | str | 是 | `拉格朗日粒子轨迹数据` | 来源与数据版本 |
| 数据契约 | `{DATA_CONTRACT}` | object | 否 | {"input_fields": [], "target_fields": [], "units": {}, "coordinates": "dataset_native"} | 变量单位网格定义 |

**输出**：dataset_manifest.json、data_contract.json、data_audit.md

**质量门禁**：
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏

**操作指令**：`读取{DATASET_PATH}中的{DATASET_NAME}，为“E3等变粒子网络拉格朗日流体模拟”建立数据清单。检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可，按{DATA_CONTRACT}输出机器可读契约。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

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

**目的**：训练E3-equivariant GNN、Lagrangian simulator完成指定输入到目标物理量的映射。

**依赖步骤**：s02

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 模型名称 | `{MODEL_NAME}` | str | 是 | `E3-equivariant GNN、Lagrangian simulator` | 实现或模型注册名 |
| 训练配置 | `{TRAIN_CONFIG}` | object | 是 | {"framework": "PyTorch", "epochs": 100, "batch_size": 8, "learning_rate": 0.001, "seed": 42, "early_stopping_patience": 15} | 超参数和随机种子 |
| 初始权重 | `{INIT_CHECKPOINT}` | doc | 否 | — | 可选预训练权重 |

**输出**：best_checkpoint.pt、train_config.json、training_metrics.csv、environment.txt

**质量门禁**：
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

**操作指令**：`使用{MODEL_NAME}，默认E3-equivariant GNN、Lagrangian simulator，和{TRAIN_CONFIG}训练“E3等变粒子网络拉格朗日流体模拟”模型。加载s02切分与统计量，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。若提供{INIT_CHECKPOINT}须检查结构兼容性。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

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

1. **Learning Lagrangian Fluid Mechanics with E(3)-Equivariant Graph Neural Networks** — [sha256:50d0e267ba5e452f3f2521c406cd11ce3c04bbe4a608d7a3b3ac5406baaed15d](https://arxiv.org/abs/2305.15603)
2. **DEL_ Discrete Element Learner for Learning 3D Particle Dynamics with Neural Rendering** — sha256:06f3331276f4530f5a3ff3b7be8d00c21c4c3b5669b36c3a6475782c6802c6eb
3. **Learning Physical Models that Can Respect Conservation Laws** — sha256:fb74b0e66548e9f323e7f468917a847737e2c9b6e6eccae39289eb41c4eb6d23
4. **Modeling Dynamics over Meshes with Gauge Equivariant Nonlinear Message Passing** — sha256:55ea805c95c5c4bf2a1f15e6dd6579a5be0ebf4615d001d00136758b28c2ba6a
5. **Incorporating Symmetry into Deep Dynamics Models for Improved Generalization** — [sha256:47292e73b33f156fa86cfb7d92c5b09ee9ffb7c5d64b352e953aee7f662d16ac](https://arxiv.org/abs/2002.03061)
6. **LagrangeBench_ A Lagrangian Fluid Mechanics Benchmarking Suite** — [sha256:faaa5081925facf9d747b7865377bdd673c1b3150545a63115c0f7c79e3c8612](https://arxiv.org/abs/1806.01261)
7. **Symmetric Basis Convolutions for Learning Lagrangian Fluid Mechanics** — sha256:23299e31f91cf8d84454df2af1b46eb4bda629ad0c53c34dc63f4620ba4b3da1
