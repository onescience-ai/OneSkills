# 数据驱动RANS雷诺应力与涡黏闭合（CFD_S073）

## 任务描述

面向DNS与RANS配对湍流闭合数据完成数据驱动RANS雷诺应力与涡黏闭合。产出可复现模型、任务结果、物理一致性评估和适用域报告；域外工况需经CFD复核。

## 工作流

### 步骤 1：数据接入与契约核验

**目的**：接入DNS与RANS配对湍流闭合数据，核验样本、变量、单位、网格坐标及许可。

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 数据集路径 | `{DATASET_PATH}` | doc | 是 | — | 目录或清单文件 |
| 数据集名称 | `{DATASET_NAME}` | str | 是 | `DNS与RANS配对湍流闭合数据` | 来源与数据版本 |
| 数据契约 | `{DATA_CONTRACT}` | object | 否 | {"input_fields": [], "target_fields": [], "units": {}, "coordinates": "dataset_native"} | 变量单位网格定义 |

**输出**：dataset_manifest.json、data_contract.json、data_audit.md

**质量门禁**：
- 数据文件可读且样本可追溯
- 输入目标变量单位坐标定义完整
- 不存在训练测试泄漏

**操作指令**：`读取{DATASET_PATH}中的{DATASET_NAME}，为“数据驱动RANS雷诺应力与涡黏闭合”建立数据清单。检查文件可读性、样本数、输入与目标变量、单位、坐标系、网格拓扑、时间或工况范围、缺失值和使用许可，按{DATA_CONTRACT}输出机器可读契约。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

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

**目的**：训练Tensor-basis neural network、Symbolic closure model完成指定输入到目标物理量的映射。

**依赖步骤**：s02

| 参数 | 变量名 | 类型 | 必填 | 默认值 | 说明 |
|---|---|---|---|---|---|
| 模型名称 | `{MODEL_NAME}` | str | 是 | `Tensor-basis neural network、Symbolic closure model` | 实现或模型注册名 |
| 训练配置 | `{TRAIN_CONFIG}` | object | 是 | {"framework": "PyTorch", "epochs": 100, "batch_size": 8, "learning_rate": 0.001, "seed": 42, "early_stopping_patience": 15} | 超参数和随机种子 |
| 初始权重 | `{INIT_CHECKPOINT}` | doc | 否 | — | 可选预训练权重 |

**输出**：best_checkpoint.pt、train_config.json、training_metrics.csv、environment.txt

**质量门禁**：
- 训练验证损失均为有限值
- 最佳权重可重新加载
- 配置环境随机种子可复现

**操作指令**：`使用{MODEL_NAME}，默认Tensor-basis neural network、Symbolic closure model，和{TRAIN_CONFIG}训练“数据驱动RANS雷诺应力与涡黏闭合”模型。加载s02切分与统计量，记录代码版本、依赖、随机种子、逐轮训练验证指标与最佳权重。若提供{INIT_CHECKPOINT}须检查结构兼容性。缺少必填输入时返回BLOCKED并列出缺项，不得编造数据、权重、工况或结果。`

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

1. **Quantifying model form uncertainty in Reynolds-averaged turbulence models with Bayesian deep neural networks** — [sha256:6b1a01ddadd8d15975f967b255e6894495887ed2f5e10e0f00f516cb1498e799](https://arxiv.org/abs/1807.02901)
2. **Machine learning for RANS turbulence modeling of variable property flows** — [sha256:8931ec06739e58c1b3313d2094ff7538ffee2147b3463c0d75d13a64b19edb53](https://arxiv.org/abs/2210.15384)
3. **Deep Learning Methods for Reynolds-Averaged Navier–Stokes Simulations of Airfoil Flows** — [sha256:7db3f889b18f771b108c92ed51173f10d5a8e5823e0746eef7f31fb28304b1b8](https://arxiv.org/abs/1810.08217)
4. **Data-driven nonlinear turbulent flow scaling with Buckingham Pi variables** — [sha256:fba71d8ffaf2811b6eefb87958882e2ee335029e3b895327d00c6aaabc9b4724](https://arxiv.org/abs/2402.17990)
5. **Turbulence model augmented physics-informed neural networks for mean-flow reconstruction** — [sha256:11cb5a3f6309c5451ede7569c46f01e4f54ac9cdfd2966a40d1a43d701b779fa](https://arxiv.org/abs/2306.01065)
6. **Predictions of turbulent shear flows using deep neural networks** — [sha256:c2b3b88511b296c67316d4034fc38c209708a8bcb2c2735dfc5bd108db58f8c3](https://arxiv.org/abs/1905.03634)
7. **Machine-Learning-Augmented Predictive Modeling of Turbulent Separated Flows over Airfoils** — [sha256:6e5776281a80ca66c70adc01a87796d3b115aa2b30b47e7c6bf084af90d44133](https://arxiv.org/abs/1608.03990)
8. **Physics-informed machine learning approach for augmenting turbulence models_ A comprehensive framework** — [sha256:d0e68acc132358fdc9246c25223eb67eb82502e7ceeb8a3e2483af9d2405ef8c](https://arxiv.org/abs/1701.07102)
9. **RANS turbulence model development using CFD-driven machine learning** — [sha256:405a20d0acd29dba81ff411028839f34842983c8cc55fbf8b492b82df3eab809](https://arxiv.org/abs/1902.09075)
10. **From Bypass Transition to Flow Control and Data-Driven Turbulence Modeling_ An Input–Output Viewpoint** — [sha256:c99b31d9d43b0bf1587b12954b95cb6a1226ccc9dcf68724b68411f0f3352aa8](https://arxiv.org/abs/2003.10104)
11. **Perspectives on machine learning-augmented Reynolds-averaged and large eddy simulation models of turbulence** — [sha256:5976066ec2c104f6b75fe842d0b13759c380939e7d56d49bfa238bd22a8dc6fb](https://doi.org/10.1103/PhysRevFluids.6.050504)
12. **Discovering explicit Reynolds-averaged turbulence closures for turbulent separated flows through deep learni** — [sha256:9945175a14ca6ec8da65b4f1358c022de32e21aae21defa9c60381c74fe4eda9](https://arxiv.org/abs/2301.09048)
13. **FoilDiff_ A Hybrid Transformer Backbone for Diffusion-based Modelling of 2D Airfoil Flow Fields** — [sha256:10a29a70146d45cdee988e0e02015704afdade4a8437e3ded0dc0fd96e37be99](https://arxiv.org/abs/2510.04325)
14. **A Symplectic Theory of Turbulence Closure_ Hidden Reservoir Dynamics, Endogenous Stochastic Transport, and Kraichnan Dual Cascades** — [sha256:d89063d3a9545026bbf1f53dbd8a70f1e128c26f132f49225ec8114c0207417a](https://arxiv.org/abs/2608.06606)
15. **A high-fidelity numerical database for free-stream transition** — [sha256:eb529ea8b58f623cf143c964058e5665538304815554d4ccdf4fd44213ca0184](https://arxiv.org/abs/2606.20139)
16. **Learning Turbulence Closures with Physics-Informed Neural Networks for the Rayleigh-Taylor Transition to Turbulence** — [sha256:ab1e5cff883bb93d515f3df2ac64d5236e61ad9c72428c1c37430136b0fb021c](https://arxiv.org/abs/2607.07020)
17. **Towards bridging the gap between data-driven and theoretical turbulence closures in stratified flows** — [sha256:6d1e1be04f1de2743adce3f2d096f9efdfc3251c760fde3d15654accce08773c](https://arxiv.org/abs/2606.20901)
18. **VATO_ A Vortex-Force-Aware Transformer Operator for Unsteady Separated Aerofoil Flows** — [sha256:d13b43034c7a912dfe75637e2283531ef4fee9d3c7c9931829c72e5987fda41f](https://arxiv.org/abs/2609.00507)
