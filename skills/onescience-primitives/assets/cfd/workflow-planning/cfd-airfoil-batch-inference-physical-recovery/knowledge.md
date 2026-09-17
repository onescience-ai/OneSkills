# 批量推理与物理恢复任务

## 适用范围
本任务适用于在独立测试集上进行批量推理，并恢复原始单位、网格和物理派生量。

## 输入
- 模型权重（best_checkpoint.pt）
- 计算设备（CPU或CUDA）
- 推理批大小
- 测试集清单
- 归一化统计量
- 数据契约

## 输出
- 预测结果目录（predictions/）
- 推理清单（inference_manifest.json）
- 推理耗时（timing.csv）

## 流程节点
1. 加载模型权重
2. 加载测试集清单
3. 按批大小进行推理
4. 反归一化预测结果
5. 恢复物理单位、坐标网格
6. 恢复边界掩膜及任务派生量
7. 保存逐样本结果和耗时

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 模型权重 | best_checkpoint.pt | [场景需求书] | 默认权重 |
| 计算设备 | cuda | [场景需求书] | 默认设备 |
| 推理批大小 | 8 | [场景需求书] | 默认配置 |

## 边界与分流
- 预测结果为NaN或Inf：检查模型权重或数据。
- 单位恢复错误：检查归一化统计量与数据契约。
- 网格坐标错误：检查数据预处理步骤。
- 使用测试标签修正：禁止此操作，确保公平评估。

## 质量检查
- 预测无NaN或Inf且形状单位正确。
- 每个测试样本有唯一结果。
- 推理未使用测试目标校正。

## 回退策略
- 推理失败：检查模型权重与计算设备。
- 单位恢复错误：重新计算归一化统计量。
- 网格坐标错误：检查数据预处理步骤。

## 资源召回建议
当用户需要进行批量推理与物理恢复时，可召回本任务卡片。配套资源包括：
- 模型推理工具
- 反归一化工具
- 物理单位恢复工具
- 推理计时工具

## 证据来源
[1] A Kernel-based Resource-efficient Neural Surrogate for Multi-fidelity Prediction of Aerodynamic Field, arXiv:2512.10287, 2025
[2] AFBench_ A Large-scale Benchmark for Airfoil Design, arXiv:1411.1784, 2014
[3] Airfoil optimization using Design-by-Morphing with minimized design-space dimensionality, arXiv:2510.16020, 2025
[4] Predictive Criteria for Electrospray-Assisted Droplet Dynamics in Aerodynamic Flow Fields, arXiv:2509.22676, 2025
[5] AeroJEPA_ Learning Semantic Latent Representations for Scalable 3D Aerodynamic Field Modeling, arXiv:2605.05586, 2026
[6] AirfoilGen_ A valid-by-construction and performance-aware latent diffusion model for airfoil generation, arXiv:2605.20303, 2026