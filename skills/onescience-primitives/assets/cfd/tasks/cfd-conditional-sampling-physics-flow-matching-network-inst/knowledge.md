# 实例任务：条件采样与物理一致性筛选 @ CFD_S092

- domain: cfd
- 骨架: cfd-conditional-sampling-physics-consistency-filtering-task
- 场景: cfd-flow-matching-network-complex-flow-probability-surrogate-scenario (CFD_S092)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- CFD_S092
- 关联论文: Switched Flow Matching_ Eliminating Singularities via Switching ODEs | doi:; Physics vs Distributions_ Pareto Optimal Flow Matching with Physics Constraints | doi:; Dflow-SUR_ Enhancing Generative Aerodynamic Inverse Design using Differentiation Throughout Flow Matching | doi:; GeoFunFlow-3D_ A Physics-Guided Generative Flow Matching Framework for High-Fidelity 3D Aerodynamic Inference over Complex Geometries | doi:; Physics-Guided Generative Surrogates for Parametric Rarefied Flows with Neural-Field Auto-Decoders_ A Pipeline-Level Study of Flow Matching and Diffusion | doi:

## 本实例步骤描述
按工况生成多样流场样本并依据物理残差筛选。

## 本实例执行 prompt
加载{CHECKPOINT}，对每个测试条件生成多随机种子样本，保存采样轨迹、条件和随机种子。恢复物理量后计算边界、守恒与方程残差，剔除不合格样本并评估分布覆盖；禁止用单个漂亮样本代表整体性能。

## 本实例输入槽
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=通过训练门限权重 | default=best_checkpoint.pt
- {DEVICE} | required=True | type=str | var_name=计算设备 | hint=CPU或CUDA设备 | default=cuda
- {BATCH_SIZE} | required=False | type=int | var_name=推理批大小 | hint=按显存调整批量 | default=8

## 本实例产出
- generated_samples/
- physics_filter.json
- distribution_metrics.json

## 本实例质量门禁
- 样本条件与随机种子可追溯
- 多样性和真实性同时评价
- 物理筛选前后统计均报告

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
