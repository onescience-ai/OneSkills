# 实例任务：三维分子生成与采样 @ B52

- domain: bio
- 骨架: bio-3d-molecular-generation-sampling-task
- 场景: bio-molecular-latent-space-diffusion-evolution-and-multi-site-scenario (B52)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- B52
- 关联论文: Apo2Mol: 3D Molecule Generation via Dynamic Pocket-Aware Diffusion Models | doi:; ActivityDiff: a diffusion model with positive and negative activity guidance for de novo drug design | doi:; MolSculptor: a diffusion-evolution framework for multi-site inhibitor design | doi:

## 本实例步骤描述
生成分子拓扑和构象并记录随机性参数。

## 本实例执行 prompt
运行分子潜空间扩散进化与多位点抑制剂设计，以温度{TEMPERATURE}和种子{SEED}生成{NUM_MOLECULES}个分子及三维构象。

## 本实例输入槽
- {NUM_MOLECULES} | required=True | type=int | var_name=生成分子数 | hint=设置生成候选数量 | default=1000
- {TEMPERATURE} | required=False | type=float | var_name=采样温度 | hint=控制生成分布宽度 | default=1
- {SEED} | required=False | type=int | var_name=随机种子 | hint=固定随机采样结果 | default=42

## 本实例产出
- 候选分子SDF
- 生成轨迹
- 模型分数

## 本实例质量门禁
- 生成数量达标
- 原子坐标为有限值
- 每个分子可被化学解析

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
