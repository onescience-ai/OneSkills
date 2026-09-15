# 实例任务：候选生成与约束优化 @ CFD_S030

- domain: cfd
- 骨架: tk-cfd-6d2108f0
- 场景: sc-872969b0 (CFD_S030)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- CFD_S030
- 关联论文: G-Adaptivity_ optimised graph-based mesh relocation for finite element methods | doi:; Towards Universal Mesh Movement Networks | doi:

## 本实例步骤描述
围绕目标性能生成候选，执行约束优化并保留完整搜索轨迹。

## 本实例执行 prompt
加载{CHECKPOINT}和数据契约，将{TARGET_FIELDS}解释为优化目标与约束，执行可复现的候选生成和优化搜索。保存每次评估、可行性、目标值及Pareto前沿；不得把代理预测直接当作高保真认证结果。

## 本实例输入槽
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=通过训练门限权重 | default=best_checkpoint.pt
- {DEVICE} | required=True | type=str | var_name=计算设备 | hint=CPU或CUDA设备 | default=cuda
- {BATCH_SIZE} | required=False | type=int | var_name=推理批大小 | hint=按显存调整批量 | default=8

## 本实例产出
- design_candidates/
- optimization_history.csv
- pareto_front.json

## 本实例质量门禁
- 候选满足几何和物理硬约束
- 优化轨迹与随机种子完整
- 最优候选未混用测试标签

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
