# 谱增强PINN高频多尺度PDE求解（CFD_S042）

## 任务描述

面向高频与多尺度PDE配点完成谱增强PINN高频多尺度PDE求解。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流

### 步骤 1：数据接入与契约核验

**目的**：接入高频与多尺度PDE配点，核验样本、变量、单位、网格坐标及许可。

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 数据集路径 | `{DATASET_PATH}` | doc | 是 | — | 目录或清单文件 |
| 数据集名称 | `{DATASET_NAME}` | str | 是 | `高频与多尺度PDE配点` | 来源与数据版本 |
| 数据契约 | `{DATA_CONTRACT}` | object | 否 | {"input_fields": [], "target_fields": [], "units": {}, "coordinates": "dataset_native"} | 变量单位网格定义 |

**输出**：dataset_manifest.json、data_contract.json、data_audit.md

**质量门禁**：
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏

**操作指令**：`读取{DATASET_PATH}中的{DATASET_NAME}，为"谱增强PINN高频多尺度PDE求解"建立数据清单。检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可，按{DATA_CONTRACT}输出机器可读契约。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

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

**目的**：训练Spectral PINN、SIREN完成指定输入到目标物理量的映射。

**依赖步骤**：s02

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 模型名称 | `{MODEL_NAME}` | str | 是 | `Spectral PINN、SIREN` | 实现或模型注册名 |
| 训练配置 | `{TRAIN_CONFIG}` | object | 是 | {"framework": "PyTorch", "epochs": 100, "batch_size": 8, "learning_rate": 0.001, "seed": 42, "early_stopping_patience": 15} | 超参数和随机种子 |
| 初始权重 | `{INIT_CHECKPOINT}` | doc | 否 | — | 可选预训练权重 |

**输出**：best_checkpoint.pt、train_config.json、training_metrics.csv、environment.txt

**质量门禁**：
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

**操作指令**：`使用{MODEL_NAME}，默认Spectral PINN、SIREN，和{TRAIN_CONFIG}训练"谱增强PINN高频多尺度PDE求解"模型。加载s02切分与统计量，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。若提供{INIT_CHECKPOINT}须检查结构兼容性。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

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

## 补充知识（基于最新文献）

### 频谱偏差问题与缓解策略

频谱偏差是神经网络在学习高频分量时存在的固有偏差，低频分量学习得更快。根据最新研究[1]，频谱偏差不仅是表征限制，还与优化动力学和基于物理的损失函数设计密切相关。

**关键发现**：
- 二阶优化方法可以显著改变频谱学习顺序，使高频模态更早、更准确地恢复[1]
- Fourier特征嵌入可以丰富潜在空间，使网络能够学习高频分量[2]
- 正弦激活函数（如SIREN）可以提高网络对高频特征的表达能力[3]
- 频率分解策略将解分解为低频和高频分量，分别处理，可以提高高频问题的准确性[4]

### 谱增强PINN架构规格

**Spectral PINN**：
- 使用Fourier特征映射将输入坐标映射到高维频域空间
- 通过可学习的频率参数自适应调整频谱覆盖
- 适合处理高频振荡解

**SIREN（Sinusoidal Representation Networks）**：
- 使用正弦激活函数替代ReLU等标准激活函数
- 能够自然表示高频振荡函数
- 初始化策略对性能有重要影响[3]

### 配点采样策略

**自适应配点采样**：
- 基于残差梯度自适应调整配点密度
- 在高频区域增加配点密度以提高分辨率
- 使用多网格策略从粗到细逐步增加配点[5]

**频谱感知采样**：
- 根据目标解的频谱特性设计采样策略
- 在高频分量丰富的区域增加采样密度
- 使用归一化累积功率谱密度（NCPSD）指导采样[6]

### PDE残差计算方法

**谱方法增强的自动微分**：
- 使用Fourier变换计算频域导数
- 结合自动微分和谱方法提高导数计算精度
- 特别适合周期性边界条件和高频问题[7]

**残差加权策略**：
- 对不同频率分量的残差赋予不同权重
- 强调高频分量的残差以缓解频谱偏差
- 使用自适应权重调整策略[8]

### 无量纲化与量纲分析

**高频多尺度场景的无量纲化**：
- 对空间和时间坐标进行适当的缩放
- 考虑不同频率分量的特征尺度
- 保持物理量的量纲一致性[9]

### 验收门限

**边界残差验收**：
- 边界条件误差应小于相对误差门限的1/10
- 周期性边界条件应满足周期性约束
- Neumann边界条件的法向导数误差应小于规定阈值

**守恒误差验收**：
- 质量、动量、能量等守恒量的误差应小于规定阈值
- 对于可压缩流动，应检查质量、动量和能量守恒
- 对于不可压缩流动，应检查质量守恒和散度为零条件

## 关联文献

1. **Spectral bias in physics-informed and operator learning: Analysis and mitigation guidelines** — arXiv:2602.19265, 2026
2. **Alternating Levenberg-Marquardt Training of Physics-Informed Neural Networks with Fourier-Enhanced Features** — arXiv:2608.05892, 2026
3. **Simple initialization and parametrization of sinusoidal networks via their kernel bandwidth** — arXiv:2211.14503, 2022
4. **When Does Frequency Decomposition Benefit Physics-Informed Neural Networks? A Preliminary Ablation Study** — arXiv:2608.24940, 2026
5. **A new strategy for physics-informed neural networks based on hierarchical collocation point refinement** — arXiv:2607.14665, 2026
6. **RUNNs: Ritz-Uzawa Neural Networks for Solving Variational Problems** — arXiv:2603.12982, 2026
7. **Multi-Scale Separable Fourier Neural Networks for Solving High-Frequency PDEs** — arXiv:2605.31027, 2026
8. **RepNN: Tackling spectral bias in deep neural networks via parameter reparameterization** — arXiv:2606.16575, 2026
9. **Separated-Variable Spectral Neural Networks: A Physics-Informed Learning Approach for High-Frequency PDEs** — arXiv:2508.00628, 2025