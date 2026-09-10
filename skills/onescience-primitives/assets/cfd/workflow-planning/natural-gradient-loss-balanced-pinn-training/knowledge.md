# 自然梯度与损失平衡PINN稳定训练（CFD_S043）

## 任务描述

面向PINN基准方程与训练诊断数据完成自然梯度与损失平衡PINN稳定训练。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流

### 步骤 1：数据接入与契约核验

**目的**：接入PINN基准方程与训练诊断数据，核验样本、变量、单位、网格坐标及许可。

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 数据集路径 | `{DATASET_PATH}` | doc | 是 | — | 目录或清单文件 |
| 数据集名称 | `{DATASET_NAME}` | str | 是 | `PINN基准方程与训练诊断数据` | 来源与数据版本 |
| 数据契约 | `{DATA_CONTRACT}` | object | 否 | {"input_fields": [], "target_fields": [], "units": {}, "coordinates": "dataset_native"} | 变量单位网格定义 |

**输出**：dataset_manifest.json、data_contract.json、data_audit.md

**质量门禁**：
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏

**操作指令**：`读取{DATASET_PATH}中的{DATASET_NAME}，为“自然梯度与损失平衡PINN稳定训练”建立数据清单。检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可，按{DATA_CONTRACT}输出机器可读契约。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

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

**目的**：训练PINN、Natural-gradient optimizer完成指定输入到目标物理量的映射。

**依赖步骤**：s02

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 模型名称 | `{MODEL_NAME}` | str | 是 | `PINN、Natural-gradient optimizer` | 实现或模型注册名 |
| 训练配置 | `{TRAIN_CONFIG}` | object | 是 | {"framework": "PyTorch", "epochs": 100, "batch_size": 8, "learning_rate": 0.001, "seed": 42, "early_stopping_patience": 15} | 超参数和随机种子 |
| 初始权重 | `{INIT_CHECKPOINT}` | doc | 否 | — | 可选预训练权重 |

**输出**：best_checkpoint.pt、train_config.json、training_metrics.csv、environment.txt

**质量门禁**：
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

**操作指令**：`使用{MODEL_NAME}，默认PINN、Natural-gradient optimizer，和{TRAIN_CONFIG}训练“自然梯度与损失平衡PINN稳定训练”模型。加载s02切分与统计量，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。若提供{INIT_CHECKPOINT}须检查结构兼容性。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

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

1. **MultiAdam_ Parameter-wise Scale-invariant Optimizer for Multiscale Training of Physics-informed Neural Networks** — sha256:2d75e04f0caf995cc0b74d1de2e80aa4eb68f81d8a3f24e8c6aa2d37d5459c37
2. **Collapsing Taylor Mode Automatic Differentiation** — [sha256:068bbdf8ac1ad2230e8e43cf13dc7a428b3ef9fe4a5ec53b16e2b16677a4b9f6](https://arxiv.org/abs/2505.13644)
3. **FP64 is All You Need_ Rethinking Failure Modes in Physics-Informed Neural Networks** — [sha256:d1bd077d80e206c69a1898c4a77c1856c630f5adec9fa1f693c94c4f8015b441](https://arxiv.org/abs/2505.10949)
4. **Improving Energy Natural Gradient Descent through Woodbury, Momentum, and Randomization** — [sha256:91a705e8ce3143924acb6a9dc23187b92298b751e77b4f4be9874f75ab0f72cc](https://arxiv.org/abs/2505.12149)
5. **Challenges in Training PINNs_ A Loss Landscape Perspective** — sha256:9c4d6741961f9fd97d92c9a20fbcb34a853a08776cfffc19f05da31520c5611b
6. **Achieving High Accuracy with PINNs via Energy Natural Gradient Descent** — sha256:8b7d18ded0f547713baceaeefb704732ca41a033ee0229ae42a02f9026d7282d
7. **Gradient Descent Finds the Global Optima of Two-Layer Physics-Informed Neural Networks** — sha256:c4ca21fa616fa35aa069f584ef2ff2084c6ae0a4ffc7a60df2c87421b6e7d4b7
8. **Accelerated Training of Physics-Informed Neural Networks (PINNs) using Meshless Discretizations** — sha256:d8e816aeeb3787e922386f30b71738cde061a256cebb82370eedb446db3da20c
9. **Is L2 Physics Informed Loss Always Suitable for Training Physics Informed Neural Network** — sha256:fa0eb06603acbbf670ad33956a5226dc35e43ad68ad5224387077507264036d4
10. **Active training of physics-informed neural networks to aggregate and interpolate parametric solutions to the** — [sha256:0698a186e3bb1d8fb1826b79ed8cd9c998ba610f9f8f37a34d2505e018eb1c30](https://arxiv.org/abs/2005.05092)
11. **ConFIG_ Towards Conflict-free Training of Physics Informed Neural Networks** — [sha256:19693055bc10cf5980c36c62990fbffc37a3585daaddf987441ebedae73625b9](https://arxiv.org/abs/2306.08827)
12. **Near-optimal Sketchy Natural Gradients for Physics-Informed Neural Networks** — sha256:89bffa71af06baafb8d6b1bb48666f708967012579f2a007a77b71f8da7b7992
13. **Enhancing Stability of Physics-Informed Neural Network Training Through Saddle-Point Reformulation** — [sha256:99f17dfb5b658e1e5a665f05ecd74ec8df459d1134e31bd6b69416a13f562e51](https://arxiv.org/abs/2408.11969)
14. **Fast Convergence of Natural Gradient Descent for Over-parameterized Physics-Informed Neural Networks** — [sha256:72348d1ce051400b37e2af8adb4d6136bae5c950cc90bf8a2caa6ad5767db8b6](https://arxiv.org/abs/1905.11675)
15. **Fast training of accurate physics-informed neural networks without gradient descent** — sha256:ee5a46cdc22ef686132b956cc573e0b9fd969544c1c1f179b8889b07c7517ac7
16. **Harmonized Cone for Feasible and Non-conflict Directions in Training Physics-Informed Neural Networks** — sha256:1a15dde7dc6d2cdff8d90cfc74ab461d9ae65ae9f810cbc5e6b583f648a4a4dd
