# 骨架任务：条件采样与物理一致性筛选

- domain: cfd
- 复用场景数: 5
- 实例任务数: 5

## 步骤描述（跨场景聚合去重）
- 按工况生成多样流场样本并依据物理残差筛选。

## 执行 prompt（跨场景聚合去重）
- 加载{CHECKPOINT}，对每个测试条件生成多随机种子样本，保存采样轨迹、条件和随机种子。恢复物理量后计算边界、守恒与方程残差，剔除不合格样本并评估分布覆盖；禁止用单个漂亮样本代表整体性能。

## 输入槽（var/hint/default）
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=通过训练门限权重 | default=best_checkpoint.pt
- {DEVICE} | required=True | type=str | var_name=计算设备 | hint=CPU或CUDA设备 | default=cuda
- {BATCH_SIZE} | required=False | type=int | var_name=推理批大小 | hint=按显存调整批量 | default=8

## 产出
- distribution_metrics.json
- generated_samples/
- physics_filter.json

## 质量门禁 quality_gate
- 多样性和真实性同时评价
- 样本条件与随机种子可追溯
- 物理筛选前后统计均报告

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- cfd-conditional-sampling-physics-conditional-generative-inst
- cfd-conditional-sampling-physics-flow-matching-network-inst
- cfd-conditional-sampling-physics-gan-normalizing-flow-turbule-inst
- cfd-conditional-sampling-physics-generative-model-aerodynamic-inst
- cfd-conditional-sampling-physics-physics-informed-diffusion-inst

## 复用场景
- CFD_S091
- CFD_S092
- CFD_S093
- CFD_S094
- CFD_S095
