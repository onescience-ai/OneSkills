# PDE预处理与数据切分任务

## 适用范围
适用于PDE基础模型零样本预测场景的预处理阶段，统一物理量与表示，按几何、工况或时间构造无泄漏切分。不适用于已预处理的数据或不需要切分的数据。

## 输入
- 数据契约（来自数据接入步骤）
- 切分配置（按对象工况切分）
- 目标变量（待预测物理量）
- 是否无量纲化（统一跨工况量纲）

## 输出
- train_manifest.json（训练集清单）
- validation_manifest.json（验证集清单）
- test_manifest.json（测试集清单）
- normalization.json（归一化统计量）

## 流程节点
依据数据契约完成质控 → 重采样或图构建 → 掩膜 → 归一化或无量纲化 → 按几何、完整轨迹或物理工况为单位切分 → 保存统计量与可逆变换

## 关键参数
| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 切分配置 | 0.7/0.15/0.15 | 场景需求书 | 训练/验证/测试比例 |
| 目标变量 | 必填 | 场景需求书 | 待预测物理量 |
| 是否无量纲化 | true | 场景需求书 | 统一跨工况量纲 |
| 随机种子 | 42 | 场景需求书 | 可复现性保证 |

## 边界与分流
- **切分配置缺失**：使用默认比例。
- **目标变量未定义**：从数据契约中提取。
- **数据量不足**：调整切分比例或使用交叉验证。

## 质量检查
- 三份切分的对象轨迹互斥
- 仅用训练集计算变换统计量
- 边界与掩膜语义未破坏

## 回退策略
- 切分不互斥：重新定义切分单元，确保无重叠。
- 归一化统计量污染：重新计算，仅使用训练集。

## 资源召回建议
当用户需要进行PDE基础模型零样本预测的预处理时召回本卡片。配套资源包括：数据预处理脚本、切分工具、归一化工具。

## 补充证据（开源文档/用户自有，可选）
无

## 证据来源
[1] Zebra: In-Context Generative Pretraining for Solving Parametric PDEs, Louis Serrano et al., arXiv, 2024, DOI: 10.48550/arXiv.2410.03437
[2] Physics-informed Temporal Alignment for Auto-regressive PDE Foundation Models, 2024
[3] Zero-shot forecasting of chaotic systems, 2024
[4] Multiple Physics Pretraining for Spatiotemporal Surrogate Models, 2024
[5] MetaPhysiCa: Improving OOD Robustness in Physics-informed Machine Learning, 2024
[6] FLUID-LLM: Learning Computational Fluid Dynamics with Spatiotemporal-aware Large Language Models, Max Zhu et al., arXiv, 2024, DOI: 10.48550/arXiv.2406.04501