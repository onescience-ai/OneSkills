# 骨架任务：候选生成与约束优化

- domain: cfd
- 复用场景数: 7
- 实例任务数: 7

## 步骤描述（跨场景聚合去重）
- 围绕目标性能生成候选，执行约束优化并保留完整搜索轨迹。

## 执行 prompt（跨场景聚合去重）
- 加载{CHECKPOINT}和数据契约，将{TARGET_FIELDS}解释为优化目标与约束，执行可复现的候选生成和优化搜索。保存每次评估、可行性、目标值及Pareto前沿；不得把代理预测直接当作高保真认证结果。

## 输入槽（var/hint/default）
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=通过训练门限权重 | default=best_checkpoint.pt
- {DEVICE} | required=True | type=str | var_name=计算设备 | hint=CPU或CUDA设备 | default=cuda
- {BATCH_SIZE} | required=False | type=int | var_name=推理批大小 | hint=按显存调整批量 | default=8

## 产出
- design_candidates/
- optimization_history.csv
- pareto_front.json

## 质量门禁 quality_gate
- 优化轨迹与随机种子完整
- 候选满足几何和物理硬约束
- 最优候选未混用测试标签

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-1612e0d1
- it-1a6c2ab1
- it-53d1f3cf
- it-908e35e9
- it-b5364c16
- it-ecd442f9
- it-fe45c2c4

## 复用场景
- CFD_S029
- CFD_S030
- CFD_S031
- CFD_S032
- CFD_S033
- CFD_S034
- CFD_S035
