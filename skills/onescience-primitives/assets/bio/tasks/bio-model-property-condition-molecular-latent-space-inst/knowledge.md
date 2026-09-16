# 实例任务：模型与性质条件准备 @ B52

- domain: bio
- 骨架: bio-model-property-condition-preparation-task
- 场景: bio-molecular-latent-space-diffusion-evolution-and-multi-site-scenario (B52)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- B52
- 关联论文: Apo2Mol: 3D Molecule Generation via Dynamic Pocket-Aware Diffusion Models | doi:; ActivityDiff: a diffusion model with positive and negative activity guidance for de novo drug design | doi:; MolSculptor: a diffusion-evolution framework for multi-site inhibitor design | doi:

## 本实例步骤描述
加载权重并编码靶点、片段和优化性质。

## 本实例执行 prompt
加载{CHECKPOINT}，编码{OBJECTIVES}性质目标，并按{KEEP_SCAFFOLD}决定是否固定种子骨架。

## 本实例输入槽
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=模型权重名称 | default=molsculptor.ckpt
- {OBJECTIVES} | required=False | type=list[str] | var_name=优化目标 | hint=列出需要优化的性质 | default=['QED', 'SA', 'affinity']
- {KEEP_SCAFFOLD} | required=False | type=bool | var_name=保留核心骨架 | hint=是否固定输入分子骨架 | default=False

## 本实例产出
- 模型加载记录
- 性质条件向量
- 骨架约束

## 本实例质量门禁
- 权重版本可追溯
- 性质定义完整
- 固定骨架原子映射有效

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
