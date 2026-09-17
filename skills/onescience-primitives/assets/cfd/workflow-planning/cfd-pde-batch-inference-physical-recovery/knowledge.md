# PDE批量推理与物理恢复任务

## 适用范围
适用于PDE基础模型零样本预测场景的推理阶段，在独立测试集推理，恢复原始单位、网格和物理派生量。不适用于训练阶段或验证阶段。

## 输入
- 模型权重（通过训练门限权重）
- 计算设备（CPU或CUDA设备）
- 推理批大小（按显存调整批量）
- 测试数据（来自预处理步骤）
- 数据契约（来自数据接入步骤）

## 输出
- predictions/（预测结果目录）
- inference_manifest.json（推理清单）
- timing.csv（推理耗时）

## 流程节点
加载模型权重及训练时数据契约 → 在独立测试集上推理 → 反归一化并恢复物理单位、坐标网格、边界掩膜及任务派生量 → 保存逐样本结果和耗时

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 模型权重 | best_checkpoint.pt | 场景需求书 | 通过训练门限权重 |
| 计算设备 | cuda | 场景需求书 | CPU或CUDA设备 |
| 推理批大小 | 8 | 场景需求书 | 按显存调整批量 |

## 边界与分流
- **预测出现NaN或Inf**：检查数据预处理、模型数值稳定性，必要时使用混合精度训练。
- **形状单位不正确**：检查数据契约和反归一化流程。
- **测试目标泄露**：确保推理未使用测试目标校正。

## 质量检查
- 预测无NaN或Inf且形状单位正确
- 每个测试样本有唯一结果
- 推理未使用测试目标校正

## 回退策略
- 推理失败：检查模型权重、数据加载，必要时降低批大小。
- 物理恢复错误：重新检查数据契约和反归一化步骤。

## 资源召回建议
当用户需要进行PDE基础模型零样本预测的推理时召回本卡片。配套资源包括：推理脚本、反归一化工具、计时工具。

## 补充证据（开源文档/用户自有，可选）
无

## 证据来源
[1] Zebra: In-Context Generative Pretraining for Solving Parametric PDEs, Louis Serrano et al., arXiv, 2024, DOI: 10.48550/arXiv.2410.03437
[2] Physics-informed Temporal Alignment for Auto-regressive PDE Foundation Models, 2024
[3] Zero-shot forecasting of chaotic systems, 2024
[4] Multiple Physics Pretraining for Spatiotemporal Surrogate Models, 2024
[5] MetaPhysiCa: Improving OOD Robustness in Physics-informed Machine Learning, 2024
[6] FLUID-LLM: Learning Computational Fluid Dynamics with Spatiotemporal-aware Large Language Models, Max Zhu et al., arXiv, 2024, DOI: 10.48550/arXiv.2406.04501