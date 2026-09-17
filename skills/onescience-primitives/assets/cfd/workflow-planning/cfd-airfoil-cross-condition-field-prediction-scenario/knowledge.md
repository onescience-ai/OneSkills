# 核方法与生成模型翼型跨工况场预测场景

## 适用范围
本场景适用于基于核方法与生成模型的翼型跨工况场预测任务，针对参数化翼型多工况与多保真数据，旨在构建可复现的预测模型，并输出物理一致性评估和适用域报告。域外工况需经CFD复核。

## 输入
- 参数化翼型几何数据
- 多工况流场数据（不同雷诺数、攻角等）
- 多保真数据（如实验数据、高精度CFD数据、低精度代理模型数据）
- 数据契约（变量、单位、网格定义）

## 输出
- 可复现的预测模型（核方法代理模型、扩散模型）
- 预测场结果（压力、速度等物理量）
- 物理一致性评估报告（守恒性、边界条件满足等）
- 适用域报告（模型可靠工作的工况范围）
- 域外工况复核建议

## 流程节点
1. 数据接入与契约核验 → 2. 预处理与数据切分 → 3. 模型配置与训练 → 4. 批量推理与物理恢复 → 5. 任务验收与适用域判定

每步含：操作、参数、工具、质量门禁（详见workflow卡片）

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 模型类型 | Kernel surrogate, Diffusion model | [场景需求书] | 核方法与生成模型 |
| 数据切分比例 | train: 0.7, validation: 0.15, test: 0.15 | [场景需求书] | 默认配置 |
| 验收指标 | relative_L2, RMSE, conservation_residual, boundary_error | [场景需求书] | 统计与物理指标 |
| 相对误差门限 | 0.1 | [场景需求书] | 默认阈值 |

## 边界与分流
- 域外工况：超出模型适用域的工况需进行CFD复核，不得直接信任模型预测。
- 数据不足：多保真数据融合时，若某保真度数据缺失，需评估对模型性能的影响。
- 模型不收敛：训练过程中若验证损失不下降，需调整超参数或检查数据质量。
- 物理不一致：预测结果违反物理约束（如质量不守恒），需重新审查模型或数据。

## 质量检查
- 数据完整性：所有输入变量单位、坐标系定义完整。
- 训练验证损失均为有限值。
- 预测无NaN或Inf且形状单位正确。
- 统计与物理指标同时报告。
- 最差样本可追溯。
- 结论含适用域限制与复核建议。

## 回退策略
- 若模型训练失败，可尝试简化模型或增加数据。
- 若物理一致性评估不通过，可引入物理约束或后处理修正。
- 若适用域报告表明模型不可用，需重新收集数据或调整模型架构。

## 资源召回建议
当用户需要进行翼型跨工况场预测时，可召回本场景卡片。配套资源包括：
- 数据接入与预处理工具
- 核方法代理模型实现
- 扩散模型实现
- 物理一致性评估工具
- 适用域分析工具

## 证据来源
[1] A Kernel-based Resource-efficient Neural Surrogate for Multi-fidelity Prediction of Aerodynamic Field, arXiv:2512.10287, 2025
[2] AFBench_ A Large-scale Benchmark for Airfoil Design, arXiv:1411.1784, 2014
[3] Airfoil optimization using Design-by-Morphing with minimized design-space dimensionality, arXiv:2510.16020, 2025
[4] Predictive Criteria for Electrospray-Assisted Droplet Dynamics in Aerodynamic Flow Fields, arXiv:2509.22676, 2025
[5] AeroJEPA_ Learning Semantic Latent Representations for Scalable 3D Aerodynamic Field Modeling, arXiv:2605.05586, 2026
[6] AirfoilGen_ A valid-by-construction and performance-aware latent diffusion model for airfoil generation, arXiv:2605.20303, 2026