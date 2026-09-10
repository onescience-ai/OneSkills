# 物理信息网络稀疏观测参数反演（CFD_S038）

## 任务描述

面向稀疏流场观测与未知PDE参数完成物理信息网络稀疏观测参数反演。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流

### 步骤 1：数据接入与契约核验

**目的**：接入稀疏流场观测与未知PDE参数，核验样本、变量、单位、网格坐标及许可。

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 数据集路径 | `{DATASET_PATH}` | doc | 是 | — | 目录或清单文件 |
| 数据集名称 | `{DATASET_NAME}` | str | 是 | `稀疏流场观测与未知PDE参数` | 来源与数据版本 |
| 数据契约 | `{DATA_CONTRACT}` | object | 否 | {"input_fields": [], "target_fields": [], "units": {}, "coordinates": "dataset_native"} | 变量单位网格定义 |

**输出**：dataset_manifest.json、data_contract.json、data_audit.md

**质量门禁**：
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏

**操作指令**：`读取{DATASET_PATH}中的{DATASET_NAME}，为“物理信息网络稀疏观测参数反演”建立数据清单。检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可，按{DATA_CONTRACT}输出机器可读契约。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

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

**目的**：训练Inverse PINN、Physics-informed data assimilation完成指定输入到目标物理量的映射。

**依赖步骤**：s02

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 模型名称 | `{MODEL_NAME}` | str | 是 | `Inverse PINN、Physics-informed data assimilation` | 实现或模型注册名 |
| 训练配置 | `{TRAIN_CONFIG}` | object | 是 | {"framework": "PyTorch", "epochs": 100, "batch_size": 8, "learning_rate": 0.001, "seed": 42, "early_stopping_patience": 15} | 超参数和随机种子 |
| 初始权重 | `{INIT_CHECKPOINT}` | doc | 否 | — | 可选预训练权重 |

**输出**：best_checkpoint.pt、train_config.json、training_metrics.csv、environment.txt

**质量门禁**：
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

**操作指令**：`使用{MODEL_NAME}，默认Inverse PINN、Physics-informed data assimilation，和{TRAIN_CONFIG}训练“物理信息网络稀疏观测参数反演”模型。加载s02切分与统计量，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。若提供{INIT_CHECKPOINT}须检查结构兼容性。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

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

1. **Inferring flow parameters and turbulent configuration with physics-informed data assimilation and spectral n** — [sha256:0614de8966337d0985615aa20bdd7dbfd57305699e12a7405151bd2e6e5e1d2e](https://arxiv.org/abs/1804.07680)
2. **CoPINN_ Cognitive Physics-Informed Neural Networks** — sha256:a962efd8d8472f531ab1077b8892558db2f4e8ef3d878473ae9010f07e93327e
3. **Parameterized Physics-Informed Neural Networks for Parameterized PDEs** — sha256:19c134c620bfa161402df47c8fbccbe4f02e376d38232fa0b4968f72ec87bd0c
4. **RoPINN_ Region Optimized Physics-Informed Neural Networks** — sha256:d11549c11674ce7fa995c3f8de25ef69ec53d24a2c5de7e5c391c597e5cc8598
5. **Multi-output physics-informed neural networks for forward and inverse PDE problems with uncertainties** — [sha256:3fbcc429923263f72748b677bbe8185fccd4734a5ae504b8e08bdce954079972](https://arxiv.org/abs/2202.01710)
6. **Physics-informed learning of governing equations from scarce data** — [sha256:e22b2435b92838ef3bd0c34e97b6c62b51143889505369068bdf70d8e65195ed](https://arxiv.org/abs/2005.03448)
7. **Surrogate modeling for fluid flows based on physics-constrained deep learning without simulation data** — [sha256:fe779a5dc470f9578a72416f08a15c601175c0dc8c0f7be98ce4227d4f3fd685](https://arxiv.org/abs/1906.02382)
8. **Physics informed deep learning (Part I)_ Data-driven solutions of nonlinear partial differential equations** — [sha256:2a8db6776a110a4f36bd1e36af79cf31a2e74baa5af8f7ee3d9286a75fdc400d](https://arxiv.org/abs/1711.10561)
9. **Causal-PIK_ Causality-based Physical Reasoning with a Physics-Informed Kernel** — sha256:8e961b63604ce4cf39c73a3b4e78098e3af10ce51b4d13dd159d115e72c03e00
10. **DiffWind_ Physics-Informed Differentiable Modeling of Wind-Driven Object Dynamics** — [sha256:08c19254a42054b37d17ba587aa6a5b8ffb19da9a5bbdfbc893e4f99eede4306](https://arxiv.org/abs/2311.15127)
11. **Physics-informed learning under mixing_ How physical knowledge speeds up learning** — sha256:816d137d88d3032492c1e18c38d9520f94b0c80143eb34515e909f743ba9c92e
