# Physics-Informed Stochastic PDE Solver Workflow

## 适用范围
本工作流面向随机微分方程（SDE）与高维偏微分方程（PDE）的求解需求，采用物理信息驱动的方法（Physics-informed approaches）将方程约束嵌入神经网络或高斯过程训练，实现从样本数据到物理场解的映射。适用于流体力学、空气动力学、城市微气候等领域的随机PDE求解，要求输出具有物理一致性的解场并提供适用域判定。域外工况（几何/参数超出训练分布）需经传统CFD复核后方可工程部署。

## 输入
- 随机微分方程或高维PDE的训练样本（时空场数据、配点坐标、边界条件）
- 数据契约：变量名称、物理量单位、网格坐标定义
- 目标物理量（待预测场变量）

## 输出
- 求解模型（训练好的权重/checkpoint）
- 解场（solution fields）、PDE残差场、边界残差
- 物理一致性评估报告、适用域判定报告、PASS/REJECT/BLOCKED结论

## 流程节点

```
数据接入与契约核验 (s01)
  ↓
预处理与数据切分 (s02)
  ↓
模型配置与训练 (s03)
  ↓
方程求解与物理残差恢复 (s04)
  ↓
任务验收与适用域判定 (s05)
```

### s01 数据接入与契约核验
- **操作**：读取数据集，检查可读性、样本数、变量定义、单位、坐标系、网格拓扑、时间范围、缺失值和使用许可
- **质量门禁**：数据文件可读且样本可追溯；输入目标变量单位坐标定义完整；不存在训练测试泄漏
- **输出产物**：dataset_manifest.json, data_contract.json, data_audit.md

### s02 预处理与数据切分
- **操作**：完成质控、重采样、归一化或无量纲化；按几何/工况/轨迹为单位切分（不得打散同一轨迹帧）
- **质量门禁**：三份切分的对象轨迹互斥；仅用训练集计算变换统计量；边界与掩膜语义未破坏
- **输出产物**：train/val/test manifest, normalization.json

### s03 模型配置与训练
- **操作**：使用 Physics-informed stochastic solver 或 Gaussian process 训练模型，记录代码版本、依赖、随机种子、逐轮指标与最佳权重
- **质量门禁**：训练验证损失均为有限值；最佳权重可重新加载；配置环境随机种子可复现
- **输出产物**：best_checkpoint.pt, train_config.json, training_metrics.csv, environment.txt

### s04 方程求解与物理残差恢复
- **操作**：加载checkpoint，在查询配点/网格上求解目标PDE，使用自动微分或离散算子恢复导数、通量和方程残差
- **质量门禁**：解场导数与残差均为有限值；边初值逐项满足门限；独立数值解或解析解可对照
- **输出产物**：solution_fields/, pde_residuals/, boundary_residuals.csv
- **禁止事项**：禁止只依据训练损失判定方程已求解

### s05 任务验收与适用域判定
- **操作**：按验收指标（相对L2误差、PDE残差、边界误差、守恒误差）评价结果，报告最差样本和推理成本；若需外推测试则执行几何或工况外推
- **质量门禁**：统计与物理指标同时报告；最差样本可追溯；结论含适用域限制与复核建议
- **输出产物**：evaluation.json, worst_cases.csv, applicability_report.md, PASS_REJECT_BLOCKED.txt
- **判定标准**：使用 MAX_RELATIVE_L2 及任务物理门限给出 PASS、REJECT 或 BLOCKED

## 关键参数

### 通用判据（方法层，同类体系可参考）

| 参数 | 判据 | 说明 |
|------|------|------|
| 数据切分策略 | 按几何/工况/轨迹为单位 | 不得打散同一轨迹帧，防止数据泄漏 |
| 物理残差验证 | 独立数值解或解析解对照 | 不能仅凭训练损失判定求解成功 |
| 验收指标 | 同时报告统计误差与物理约束 | 相对L2、PDE残差、边界误差、守恒误差缺一不可 |
| 适用域判定 | 需包含外推测试结果 | 不得仅凭平均误差宣称工程可用 |
| 域外工况处理 | 经CFD复核后方可部署 | 域外工况不在本工作流覆盖范围内 |

### 校准数值（场景专属值，供量级校准）
以下数值来自 CFD_S046 场景，供量级校准；其他体系需以自身证据重新锚定。

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认训练epoch | 100 | 场景需求书 | PyTorch框架下默认值 |
| 默认batch_size | 8 | 场景需求书 | 按显存调整 |
| 默认学习率 | 0.001 | 场景需求书 | 标准PINN学习率 |
| early_stopping_patience | 15 | 场景需求书 | 默认早停轮数 |
| 默认MAX_RELATIVE_L2 | 0.1 | 场景需求书 | 测试集放行阈值 |
| 默认SPLIT比例 | 70/15/15 | 场景需求书 | train/val/test |

## 边界与分流

- **数据不可读或缺失必填字段**：返回 BLOCKED，列出缺项清单，不得编造数据
- **训练损失为NaN或Inf**：检查学习率、批大小、数据归一化；必要时降低学习率或增加正则化
- **物理残差不收敛**：检查PDE残差权重、网络架构、配点采样策略；考虑调整损失函数权重
- **域外工况测试失败**：明确标记为不适用，建议经传统CFD复核
- **独立解对照缺失**：标记为"验证受限"，仅报告统计误差，不给出物理一致性结论

## 质量检查
- 数据文件可读性检查
- 变量单位与坐标系一致性验证
- 训练过程收敛性监控（损失曲线、梯度范数）
- 解场有限值检查
- 边界条件逐项验证
- 守恒性/方程残差定量评估
- 最差样本追溯与分析

## 回退策略
- 训练不收敛：降低学习率、增加早停耐心、调整网络架构
- 物理残差过大：调整PDE损失权重、增加配点数量、改进采样策略
- 适用域判定REJECT：标记为不可用，建议传统CFD替代或重新设计模型

## 资源召回建议
当遇到以下需求时召回本卡片：
- 随机微分方程(SDE)求解
- 高维PDE求解
- 物理信息神经网络(PINN)训练
- 高斯过程(GP)在PDE求解中的应用
- 需要物理一致性保证的场预测任务

配套资源建议：
- 数据处理：cfd-sde-highdim-pde-data-intake, cfd-sde-highdim-pde-preprocessing-split
- 模型训练：cfd-sde-highdim-pde-model-training
- 求解验证：cfd-sde-highdim-pde-equation-solve-residual, cfd-sde-highdim-pde-task-acceptance

## 证据来源
[1] Aerodynamic force reconstruction using physics-informed Gaussian processes, arXiv:2605.22111, 2025
[2] Integration Matters for Learning PDEs with Backward SDEs, arXiv:2505.01078, 2025
[3] PIG: Physics-Informed Gaussians as Adaptive Parametric Mesh Representations, 2024
[4] Score-based free-form architectures for high-dimensional Fokker-Planck equations, 2024
[5] In-Context Learning of Stochastic Differential Equations with Foundation Inference Models, arXiv:2502.19049, 2025
[6] Learning in modal space: Solving time-dependent stochastic PDEs using physics-informed neural networks, arXiv:1905.01205, 2019
[7] Gaussian Process Priors for Systems of Linear Partial Differential Equations with Constant Coefficients, 2024
[8] Physics-informed machine learning with smoothed particle hydrodynamics, PhysRevFluids.8.054602, 2023
[9] Learning a Neural Solver for Parametric PDEs to Enhance Physics-Informed Methods, 10.1145/3620665.3640366, 2024
[10] Physics-Informed Inference Time Scaling for Solving High-Dimensional Partial Differential Equations, 2024
[11] UrbanGraph: Physics-Informed Spatio-Temporal Dynamic Heterogeneous Graphs for Urban Microclimate Prediction, 2024
[12] Physics-Informed Kolmogorov-Arnold networks for viscoelastic fluid equations, arXiv:2608.29895, 2025
