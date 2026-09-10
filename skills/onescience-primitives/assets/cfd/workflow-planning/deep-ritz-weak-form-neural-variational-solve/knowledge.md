# Deep Ritz与弱形式神经变分求解（CFD_S044）

## 任务描述

面向椭圆与演化方程变分积分数据完成Deep Ritz与弱形式神经变分求解。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流

### 步骤 1：数据接入与契约核验

**目的**：接入椭圆与演化方程变分积分数据，核验样本、变量、单位、网格坐标及许可。

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 数据集路径 | `{DATASET_PATH}` | doc | 是 | — | 目录或清单文件 |
| 数据集名称 | `{DATASET_NAME}` | str | 是 | `椭圆与演化方程变分积分数据` | 来源与数据版本 |
| 数据契约 | `{DATA_CONTRACT}` | object | 否 | {"input_fields": [], "target_fields": [], "units": {}, "coordinates": "dataset_native"} | 变量单位网格定义 |

**输出**：dataset_manifest.json、data_contract.json、data_audit.md

**质量门禁**：
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏

**操作指令**：`读取{DATASET_PATH}中的{DATASET_NAME}，为“Deep Ritz与弱形式神经变分求解”建立数据清单。检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可，按{DATA_CONTRACT}输出机器可读契约。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

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

**目的**：训练Deep Ritz network、Weak-form neural solver完成指定输入到目标物理量的映射。

**依赖步骤**：s02

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 模型名称 | `{MODEL_NAME}` | str | 是 | `Deep Ritz network、Weak-form neural solver` | 实现或模型注册名 |
| 训练配置 | `{TRAIN_CONFIG}` | object | 是 | {"framework": "PyTorch", "epochs": 100, "batch_size": 8, "learning_rate": 0.001, "seed": 42, "early_stopping_patience": 15} | 超参数和随机种子 |
| 初始权重 | `{INIT_CHECKPOINT}` | doc | 否 | — | 可选预训练权重 |

**输出**：best_checkpoint.pt、train_config.json、training_metrics.csv、environment.txt

**质量门禁**：
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

**操作指令**：`使用{MODEL_NAME}，默认Deep Ritz network、Weak-form neural solver，和{TRAIN_CONFIG}训练“Deep Ritz与弱形式神经变分求解”模型。加载s02切分与统计量，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。若提供{INIT_CHECKPOINT}须检查结构兼容性。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

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

1. **Refined generalization analysis of the Deep Ritz Method and Physics-Informed Neural Networks** — sha256:671476fad5e98c106b2c8028fd8a269d9b2b9536da6789419bc672276119a22e
2. **PINP_ Physics-Informed Neural Predictor with latent estimation of fluid flows** — [sha256:53cfbffba7df25fb2a187d9ba3ed7739c8653d33b18cc31bc1ebb4e84e2b12d2](https://arxiv.org/abs/2504.06070)
3. **Gradient Alignment in Physics-informed Neural Networks_ A Second-Order Optimization Perspective** — [sha256:3c112de95af7692fc70f9d1cae93d32d3a1daee3e5758c42fe67500abb2f5633](https://arxiv.org/abs/2502.00604)
4. **Learning from Integral Losses in Physics-Informed Neural Networks** — sha256:c6ae964c33cd5b4cd5cfe118a41aafccb89f701febb771912fad2d20428caf1d
5. **Efficient Error Certification for Physics-Informed Neural Networks** — sha256:8618ccea85d2790ff8c94357020cf900677bde0c538a1ab2f63ed9f32333bb8b
6. **Solving Poisson Equations using Neural Walk-on-Spheres** — sha256:260af15599942d99086e2f19dd0de1dab3b501240407ad0c2ea2dc487f2bd407
7. **Characteristic Neural Ordinary Differential Equation** — [sha256:dee9fe1719d5b77e341f2eaf63fcbf4faceec5374e038a00d0ca02b2f1cce550](https://arxiv.org/abs/2111.13207)
8. **Entropy-dissipation Informed Neural Network for McKean-Vlasov Type PDEs** — sha256:95c235803a003ea9761a455f1670ea532c83d66f36f861c6b5aa9a59dee4b1b5
9. **Randomized Sparse Neural Galerkin Schemes for Solving Evolution Equations with Deep Networks** — sha256:f0af75cfcb34425987ff86179d5217cdf211ca8e803f2d2ded86b9d9cbe629df
10. **Physics-informed neural networks for the shallow-water equations on the sphere** — [sha256:d658cf19da642f176f64f993a125c25dc0895bb241ca3e8f34efd3dde413a647](https://arxiv.org/abs/2104.00615)
11. **Characterizing possible failure modes in physics-informed neural networks** — [sha256:677417a271d24f3927090dfc3a1f5430baeb8d9d2943652d06639cd4db7fc30a](https://arxiv.org/abs/2109.01050)
12. **Error Analysis of Deep Ritz Methods for Elliptic Equations** — [sha256:cf9ac01f92aa7ba6ffaf479f82c604c30a5e9fc88f6bacdab30ed81e6417dd95](https://arxiv.org/abs/2107.14478)
13. **Adaptive activation functions accelerate convergence in deep and physics-informed neural networks** — [sha256:4ecc3547b58f7664e6a8124a431b60c671356f78e5dae7a0ad0071acfab70c93](https://arxiv.org/abs/1906.01170)
14. **Weak adversarial networks for high-dimensional partial differential equations** — [sha256:06b5ce437f7ebd456a83d6295f829c78ac7afabf9ecc2a93b8dc3a15648bb5a9](https://arxiv.org/abs/1907.08272)
15. **The Deep Ritz Method_ A Deep Learning-Based Numerical Algorithm for Solving Variational Problems** — [sha256:da3d20abc3c9aa279826fc9271efaf6648881c58d631c786e83ea5cae2f61031](https://arxiv.org/abs/1710.00211)
16. **The neural particle method – An updated Lagrangian physics informed neural network for computational fluid d** — [sha256:45bb8b2209fcca6667a4da37b9258fbf543f3a6d093764f3d9a93df3430716d0](https://arxiv.org/abs/2003.10208)
17. **Composing Partial Differential Equations with Physics-Aware Neural Networks** — [sha256:d1463f4dedf0b04718a0bd7b330c7db7fda0bb7040cefd8de00fe96c2f537a34](https://arxiv.org/abs/1610.10099)
18. **Physics-informed Neural Networks for Functional Differential Equations_ Cylindrical Approximation and Its Co** — [sha256:f36bad7df839c52ca3b4589ee2cfe8768309298059b22ad2c3e6261d8bf21962](https://arxiv.org/abs/1607.06450)
19. **FlashPDE_ A Drop-In Fused Triton Operator Library for Neural PDE Solvers** — [sha256:b5b81901212c8e87380d84841fd3b4a4cc64cd5a4e9fb321f8ed2e0f21b3734e](https://arxiv.org/abs/2607.18020)
