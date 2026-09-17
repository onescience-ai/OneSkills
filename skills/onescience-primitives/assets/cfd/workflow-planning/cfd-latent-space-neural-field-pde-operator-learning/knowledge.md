# 潜空间与神经场连续PDE算子学习

## 适用范围
本卡服务的问题类：面向连续坐标与压缩潜空间PDE数据，完成潜空间与神经场连续PDE算子学习，将高维PDE解场映射到低维潜空间进行算子逼近，产出可复现模型、物理一致性评估和适用域报告。适用于CFD领域中需要从连续坐标表示的PDE数据（如Navier-Stokes方程、扩散方程等）学习解算子的任务。不适用于离散网格上固定拓扑的算子学习（应选择FNO等规则网格方法），也不适用于需要实时交互的在线推理场景（推理成本超出实时约束时应评估降阶模型）。

## 输入
- **数据源**：连续坐标表示的PDE解场数据，包含空间坐标(x,y,z)、时间t、物理量场(u,v,p,T等)
- **数据格式**：支持HDF5、NetCDF、Zarr等科学数据格式，或numpy数组
- **压缩表示**：可选的潜空间编码（如PCA降维、自编码器编码），用于降低高维PDE数据的表示维度
- **预处理要求**：物理量需统一量纲，坐标系需标准化，边界条件需明确标注

## 输出
- **训练产物**：best_checkpoint.pt（模型权重）、train_config.json（训练配置）、training_metrics.csv（训练指标）
- **推理产物**：predictions/（逐样本预测结果）、inference_manifest.json（推理清单）、timing.csv（推理耗时）
- **评估产物**：evaluation.json（评估指标）、worst_cases.csv（最差样本）、applicability_report.md（适用域报告）、PASS_REJECT_BLOCKED.txt（验收结论）
- **验证标准**：相对L2误差、RMSE、守恒残差、边界误差均需满足任务门限

## 流程节点
1. **数据接入与契约核验** → 核验样本、变量、单位、网格坐标及许可，建立数据清单与机器可读契约
2. **预处理与数据切分** → 统一物理量与表示，按几何、工况或时间构造无泄漏切分
3. **模型配置与训练** → 使用Latent Neural Operator或Neural field operator完成指定输入到目标物理量的映射
4. **批量推理与物理恢复** → 在独立测试集推理，恢复原始单位、网格和物理派生量
5. **任务验收与适用域判定** → 评估统计误差、关键物理约束、泛化能力和计算收益，给出适用域限制

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 模型架构 | Latent Neural Operator / Neural field operator | 场景需求书 | 核心算子学习架构 |
| 训练框架 | PyTorch | 场景需求书 | 默认深度学习框架 |
| 训练轮数 | 100 | 场景需求书 | 默认训练轮数 |
| 批大小 | 8 | 场景需求书 | 默认训练批大小 |
| 学习率 | 0.001 | 场景需求书 | 默认学习率 |
| 早停耐心 | 15 | 场景需求书 | 验证损失不再下降时的等待轮数 |
| 相对L2误差门限 | 0.1 | 场景需求书 | 测试集放行阈值 |

## 边界与分流
- **数据为规则网格**：若数据为固定拓扑规则网格，应优先选择FNO等专用方法而非本流程
- **域外工况**：推理结果超出训练分布时，必须经CFD复核，不得直接工程应用
- **训练发散**：若训练验证损失出现NaN或Inf，需检查数据预处理、学习率设置或模型架构兼容性
- **推理无解**：若推理输出形状或单位与数据契约不匹配，需回溯检查checkpoint加载与反归一化流程

## 质量检查
- 训练验证损失均为有限值（非NaN/Inf）
- 最佳权重可重新加载并产生一致预测
- 配置环境随机种子可复现训练结果
- 预测无NaN或Inf且形状单位正确
- 每个测试样本有唯一结果，推理未使用测试目标校正
- 统计与物理指标同时报告，最差样本可追溯

## 回退策略
- 训练失败：检查数据切分是否泄漏、预处理是否正确、模型架构是否适配数据维度
- 推理失败：验证checkpoint兼容性、设备配置、批大小与显存匹配
- 验收不通过：分析最差样本特征，检查是否为域外工况或数据质量问题，必要时返回s02调整切分策略

## 资源召回建议
当用户任务涉及以下场景时应召回本卡：
- 从连续坐标PDE数据学习解算子
- 需要潜空间压缩的高维PDE问题
- 需要物理一致性评估的PDE代理模型
- 神经场在一般几何上的PDE求解
配套资源：cfd-latent-pde-data-intake-contract、cfd-latent-pde-preprocessing-splitting、cfd-latent-pde-model-training、cfd-latent-pde-batch-inference-physics-recovery、cfd-latent-pde-acceptance-applicability

## 证据来源
[1] Latent Neural Operator for Solving Forward and Inverse PDE Problems
[2] Operator Learning with Neural Fields: Tackling PDEs on General Geometries
[3] Solving High-Dimensional PDEs with Latent Spectral Models
[4] Implicit Representations via Operator Learning
[5] GNOT: A General Neural Operator Transformer for Operator Learning
[6] GridMix: Exploring Spatial Modulation for Neural Fields in PDE Modeling
[7] Neural operators meet conjugate gradients: The FCG-NO method for efficient PDE solving
[8] Meta-Auto-Decoder for Solving Parametric Partial Differential Equations
