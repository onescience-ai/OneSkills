# 高超声速与跨声速边界层湍流代理（CFD_S074）

## 任务描述

面向高超声速冷壁与跨声速机翼CFD数据完成高超声速与跨声速边界层湍流代理。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流

### 步骤 1：数据接入与契约核验

**目的**：接入高超声速冷壁与跨声速机翼CFD数据，核验样本、变量、单位、网格坐标及许可。

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 数据集路径 | `{DATASET_PATH}` | doc | 是 | — | 目录或清单文件 |
| 数据集名称 | `{DATASET_NAME}` | str | 是 | `高超声速冷壁与跨声速机翼CFD数据` | 来源与数据版本 |
| 数据契约 | `{DATA_CONTRACT}` | object | 否 | {"input_fields": [], "target_fields": [], "units": {}, "coordinates": "dataset_native"} | 变量单位网格定义 |

**输出**：dataset_manifest.json、data_contract.json、data_audit.md

**质量门禁**：
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏

**操作指令**：`读取{DATASET_PATH}中的{DATASET_NAME}，为“高超声速与跨声速边界层湍流代理”建立数据清单。检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可，按{DATA_CONTRACT}输出机器可读契约。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

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

**目的**：训练Transformer aerodynamic surrogate、Neural turbulence model完成指定输入到目标物理量的映射。

**依赖步骤**：s02

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 模型名称 | `{MODEL_NAME}` | str | 是 | `Transformer aerodynamic surrogate、Neural turbulence model` | 实现或模型注册名 |
| 训练配置 | `{TRAIN_CONFIG}` | object | 是 | {"framework": "PyTorch", "epochs": 100, "batch_size": 8, "learning_rate": 0.001, "seed": 42, "early_stopping_patience": 15} | 超参数和随机种子 |
| 初始权重 | `{INIT_CHECKPOINT}` | doc | 否 | — | 可选预训练权重 |

**输出**：best_checkpoint.pt、train_config.json、training_metrics.csv、environment.txt

**质量门禁**：
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

**操作指令**：`使用{MODEL_NAME}，默认Transformer aerodynamic surrogate、Neural turbulence model，和{TRAIN_CONFIG}训练“高超声速与跨声速边界层湍流代理”模型。加载s02切分与统计量，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。若提供{INIT_CHECKPOINT}须检查结构兼容性。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

### 步骤 4：闭合项预测与后验CFD耦合

**目的**：先验评估闭合项，再嵌入RANS或LES执行稳定后验推进。

**依赖步骤**：s03

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 模型权重 | `{CHECKPOINT}` | doc | 是 | `best_checkpoint.pt` | 通过训练门限权重 |
| 计算设备 | `{DEVICE}` | str | 是 | `cuda` | CPU或CUDA设备 |
| 推理批大小 | `{BATCH_SIZE}` | int | 否 | `8` | 按显存调整批量 |

**输出**：apriori_closure/、aposteriori_fields/、solver_stability.csv

**质量门禁**：
- 闭合张量或通量满足约束
- 后验求解无非物理解和发散
- 均值剖面与能谱均经验证

**操作指令**：`加载{CHECKPOINT}预测应力、通量或源项，先在独立快照上做先验误差和可实现性检查，再嵌入对应RANS或LES求解器执行后验推进。保存残差、能谱、统计剖面与稳定性记录。`

### 步骤 5：任务验收与适用域判定

**目的**：评估统计误差、关键物理约束、泛化能力和计算收益。

**依赖步骤**：s04

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 验收指标 | `{METRICS}` | list[str] | 是 | ["closure_RMSE", "mean_profile_error", "spectrum_error", "stability_horizon"] | 统计和物理指标 |
| 相对误差门限 | `{MAX_RELATIVE_L2}` | float | 否 | `0.1` | 测试集放行阈值 |
| 是否外推测试 | `{RUN_OOD_TEST}` | bool | 否 | true | 测试域外工况 |

**输出**：evaluation.json、worst_cases.csv、applicability_report.md、PASS_REJECT_BLOCKED.txt

**质量门禁**：
- 统计与物理指标同时报告
- 最差样本可追溯
- 结论含适用域限制与复核建议

**操作指令**：`按{METRICS}评价s04结果，至少报告逐变量误差、边界误差、守恒或方程残差、最差样本和推理成本。使用{MAX_RELATIVE_L2}及任务物理门限给出PASS、REJECT或BLOCKED。若{RUN_OOD_TEST}为true，执行几何或工况外推测试并明确适用域，不得仅凭平均误差宣称工程可用。`

## 关联文献

1. **Data-Driven Turbulence Modeling Approach for Cold-Wall Hypersonic Boundary Layers** — [sha256:b65b8711361cca68a30ce4518c1acd1c17f283cd6056e3fa8d8d865d643beab3](https://arxiv.org/abs/2406.17446)
2. **Gaussian processes at the Helm(holtz)_ A more fluid model for ocean currents** — sha256:61c9e4e219b45607602ed7013f5b238fcbdfe8984433b8b6c1b0db4cc6743156
3. **Scalable Transformer for PDE Surrogate Modeling** — [sha256:8e9a0330258c5af1e123884381ceab5b132bdd8ab60d7d8411ab4d642e135a0a](https://arxiv.org/abs/2209.04934)
4. **Aeroelastic Reduced-Order Model Differential Equations in Transonic Buffeting Flow** — [sha256:8806ddf6d331cffa573e1ab17b82797765d44665fa69d180df6750e2b3029b04](https://arxiv.org/abs/2510.22216)
5. **Compact representation of transonic airfoil buffet flows with observable-augmented machine learning** — [sha256:602a53955fa4cbd075bdaa0cd6db4888fa4145ff723c270a3be8a7d99dbeee1d](https://arxiv.org/abs/2509.17306)
6. **SuperWing_ a comprehensive transonic wing dataset for data-driven aerodynamic design** — [sha256:921a1d0d48171d2d066f2bfc4c432b6021e7ae81dc6de200e075a9f7b56b4668](https://arxiv.org/abs/2512.14397)
7. **Neural Differential Equations for Oscillatory Flows in Aeroelasticity Applied to Transonic Buffet** — [sha256:0406fbe8d6397b36218fa375d896ace921ec973ef500e499380a738916f03b34](https://arxiv.org/abs/2607.22402)
8. **SMART_ Scalable Mesh-free Aerodynamic Simulations from Raw Geometries using a Transformer-based Surrogate Model** — [sha256:344c0bfa3129c0f6f6b88b551714ace8a21a17f931f4bf704a077d60bd87c288](https://arxiv.org/abs/2601.18707)
