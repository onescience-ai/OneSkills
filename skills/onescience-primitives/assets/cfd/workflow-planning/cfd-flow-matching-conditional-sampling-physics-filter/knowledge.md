# Flow Matching 条件采样与物理一致性筛选

## 适用范围

本任务按工况条件生成多样流场样本并依据物理残差进行一致性筛选。适用于流匹配概率代理构建流程的第四阶段。核心原则：多样性和真实性同时评价，禁止用单个漂亮样本代表整体性能。物理筛选前后统计均须报告。

## 输入

- 模型权重（{CHECKPOINT}，来自阶段 3 的 best_checkpoint.pt）
- 计算设备（{DEVICE}，默认 cuda）
- 推理批大小（{BATCH_SIZE}，默认 8）
- 测试集清单（来自阶段 2）

## 输出

- generated_samples/（生成样本目录，含条件、随机种子、采样轨迹）
- physics_filter.json（物理筛选结果，含通过/剔除样本列表与残差值）
- distribution_metrics.json（分布覆盖评估，含多样性、覆盖度、分布距离）

## 流程节点

1. 加载 checkpoint 与归一化统计量
2. 对每个测试条件生成多随机种子样本
3. 保存采样轨迹、条件和随机种子（可追溯）
4. 恢复物理量（反归一化）
5. 计算边界残差（边界条件满足度）
6. 计算守恒残差（质量、动量、能量守恒）
7. 计算方程残差（控制方程满足度）
8. 剔除不合格样本
9. 评估分布覆盖（多样性、覆盖度）
10. 输出筛选结果与分布指标

## 关键参数

| 参数 | 值 | 来源 | 说明 |
|------|-----|------|------|
| 默认设备 | cuda | [场景需求书] | GPU 推理 |
| 默认批大小 | 8 | [场景需求书] | 按显存调整 |
| 多随机种子 | 多个 | [场景需求书] | 每条件多个样本评估多样性 |

## 边界与分流

- 单个漂亮样本：禁止用单样本代表整体，必须报告分布统计
- 物理筛选通过率极低（<10%）：检查物理残差计算逻辑，或放宽阈值重新评估
- 分布覆盖不足：检查训练数据覆盖范围，必要时补充数据
- 推理内存不足：减小 BATCH_SIZE

## 质量检查

- 样本条件与随机种子可追溯
- 多样性和真实性同时评价
- 物理筛选前后统计均报告
- 禁止用单个样本代表整体性能

## 回退策略

- 物理筛选通过率极低 → 检查残差计算逻辑，或放宽阈值
- 分布覆盖不足 → 检查训练数据，必要时补充
- 推理失败 → 检查 checkpoint 完整性，回退阶段 3

## 资源召回建议

当用户需要对 Flow matching model 生成的流场样本进行物理一致性评估时召回本卡片。前置步骤：cfd-flow-matching-model-training。后续步骤：cfd-flow-matching-task-acceptance-applicability。

## 证据来源

[1] Physics vs Distributions: Pareto Optimal Flow Matching with Physics Constraints, 2024
[2] Dflow-SUR: Enhancing Generative Aerodynamic Inverse Design using Differentiation Throughout Flow Matching, arXiv:2512.08336, 2025
[3] GeoFunFlow-3D: A Physics-Guided Generative Flow Matching Framework for High-Fidelity 3D Aerodynamic Inference over Complex Geometries, arXiv:2604.23350, 2026
[4] Physics-Guided Generative Surrogates for Parametric Rarefied Flows with Neural-Field Auto-Decoders: A Pipeline-Level Study of Flow Matching and Diffusion, arXiv:2608.25454, 2026
