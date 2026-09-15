# 实例任务：构象采样与打分 @ B41

- domain: bio
- 骨架: tk-bio-414155aa
- 场景: sc-4d3f17d4 (B41)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- B41
- 关联论文: DiffDock: Diffusion Steps, Twists, and Turns for Molecular Docking | doi:; AgenticPosesRanker: An Agentic AI Framework for Physically Grounded Ranking of Protein-Ligand Docking Poses | doi:

## 本实例步骤描述
采样平移、旋转和扭转自由度并输出候选得分。

## 本实例执行 prompt
运行全局盲对接构象生成与置信度排序，以种子{SEED}执行{INFERENCE_STEPS}步采样，为每个配体产生{POSES_PER_LIGAND}个姿态。

## 本实例输入槽
- {POSES_PER_LIGAND} | required=True | type=int | var_name=每配体姿态数 | hint=设置每个配体姿态数 | default=40
- {INFERENCE_STEPS} | required=False | type=int | var_name=推理步数 | hint=设置构象采样步数 | default=20
- {SEED} | required=False | type=int | var_name=随机种子 | hint=固定随机采样结果 | default=101

## 本实例产出
- 候选姿态
- 对接得分
- 采样日志

## 本实例质量门禁
- 每个成功配体有候选
- 坐标为有限值
- 配体键连接未改变

## 可调资源（edge:resource，仅真实存在）
- models/diffdock

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
