# 预处理与数据切分任务

## 适用范围
本任务适用于统一物理量与表示，按几何、工况或时间构造无泄漏切分，为模型训练提供标准化数据。

## 输入
- 数据契约（来自数据接入步骤）
- 切分配置（训练、验证、测试比例）
- 目标变量列表
- 是否无量纲化选项

## 输出
- 训练集清单（train_manifest.json）
- 验证集清单（validation_manifest.json）
- 测试集清单（test_manifest.json）
- 归一化统计量（normalization.json）

## 流程节点
1. 依据数据契约完成质控
2. 重采样或图构建
3. 掩膜处理
4. 归一化或无量纲化
5. 按几何、完整轨迹或物理工况为单位切分
6. 保存统计量与可逆变换

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 切分比例 | train: 0.7, validation: 0.15, test: 0.15 | [场景需求书] | 默认配置 |
| 随机种子 | 42 | [场景需求书] | 可复现性 |
| 分组方式 | geometry_or_trajectory | [场景需求书] | 按对象或轨迹分组 |
| 无量纲化 | true | [场景需求书] | 统一跨工况量纲 |

## 边界与分流
- 数据质量差：进行质控后重新切分。
- 切分泄漏：检查分组方式，确保同一轨迹不跨集。
- 归一化错误：仅用训练集计算统计量。
- 掩膜语义破坏：检查边界条件与掩膜定义。

## 质量检查
- 三份切分的对象轨迹互斥。
- 仅用训练集计算变换统计量。
- 边界与掩膜语义未破坏。

## 回退策略
- 切分泄漏：调整分组方式或重新设计切分策略。
- 归一化错误：重新计算统计量并验证可逆性。
- 数据质量差：返回数据接入步骤重新核验。

## 资源召回建议
当用户需要进行数据预处理与切分时，可召回本任务卡片。配套资源包括：
- 数据质控工具
- 归一化与无量纲化工具
- 数据切分工具
- 统计量保存工具

## 证据来源
[1] A Kernel-based Resource-efficient Neural Surrogate for Multi-fidelity Prediction of Aerodynamic Field, arXiv:2512.10287, 2025
[2] AFBench_ A Large-scale Benchmark for Airfoil Design, arXiv:1411.1784, 2014
[3] Airfoil optimization using Design-by-Morphing with minimized design-space dimensionality, arXiv:2510.16020, 2025
[4] Predictive Criteria for Electrospray-Assisted Droplet Dynamics in Aerodynamic Flow Fields, arXiv:2509.22676, 2025
[5] AeroJEPA_ Learning Semantic Latent Representations for Scalable 3D Aerodynamic Field Modeling, arXiv:2605.05586, 2026
[6] AirfoilGen_ A valid-by-construction and performance-aware latent diffusion model for airfoil generation, arXiv:2605.20303, 2026