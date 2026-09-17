# 核方法与生成模型翼型跨工况场预测工作流

## 适用范围
本工作流适用于基于核方法与生成模型的翼型跨工况场预测任务，从数据接入到任务验收的完整流程。

## 输入
- 参数化翼型多工况与多保真数据集路径
- 数据契约（变量、单位、网格定义）
- 切分配置（训练、验证、测试比例）
- 模型训练配置（超参数、随机种子）
- 验收指标与阈值

## 输出
- 数据清单与数据契约
- 预处理后的训练、验证、测试数据集
- 训练好的模型权重与训练日志
- 推测结果与推理日志
- 评估报告与适用域报告

## 流程节点
1. 数据接入与契约核验 → 2. 预处理与数据切分 → 3. 模型配置与训练 → 4. 批量推理与物理恢复 → 5. 任务验收与适用域判定

每步含：操作、参数、工具、质量门禁

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 数据切分比例 | train: 0.7, validation: 0.15, test: 0.15 | [场景需求书] | 默认配置 |
| 无量纲化 | true | [场景需求书] | 统一跨工况量纲 |
| 训练框架 | PyTorch | [场景需求书] | 默认框架 |
| 训练轮数 | 100 | [场景需求书] | 默认配置 |
| 批大小 | 8 | [场景需求书] | 默认配置 |
| 学习率 | 0.001 | [场景需求书] | 默认配置 |
| 早停耐心 | 15 | [场景需求书] | 默认配置 |
| 验收指标 | relative_L2, RMSE, conservation_residual, boundary_error | [场景需求书] | 统计与物理指标 |
| 相对误差门限 | 0.1 | [场景需求书] | 默认阈值 |

## 边界与分流
- 数据不可读或样本不追溯：返回BLOCKED，列出缺项。
- 训练验证损失为NaN或Inf：重新检查数据或调整超参数。
- 预测结果形状单位错误：检查数据预处理与模型输出层。
- 最差样本误差超限：分析失败原因，可能需调整模型或数据。
- 域外工况：执行外推测试并明确适用域，需CFD复核。

## 质量检查
- 数据文件可读且样本可追溯。
- 输入目标变量单位坐标定义完整。
- 不存在训练测试泄漏。
- 三份切分的对象轨迹互斥。
- 仅用训练集计算变换统计量。
- 边界与掩膜语义未破坏。
- 训练验证损失均为有限值。
- 最佳权重可重新加载。
- 配置环境随机种子可复现。
- 预测无NaN或Inf且形状单位正确。
- 每个测试样本有唯一结果。
- 推理未使用测试目标校正。
- 统计与物理指标同时报告。
- 最差样本可追溯。
- 结论含适用域限制与复核建议。

## 回退策略
- 数据接入失败：检查数据路径与格式，或联系数据提供方。
- 预处理失败：检查数据质量与切分配置。
- 模型训练失败：调整超参数、检查数据或简化模型。
- 推理失败：检查模型权重与计算设备。
- 验收不通过：分析评估报告，调整模型或数据。

## 资源召回建议
当用户需要执行翼型跨工况场预测工作流时，可召回本工作流卡片。配套资源包括：
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