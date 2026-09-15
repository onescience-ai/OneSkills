# 实例任务：分子设计目标定义 @ B51

- domain: bio
- 骨架: tk-bio-28834bb7
- 场景: sc-0825c907 (B51)
- step_id: s01
- depend: []

## 场景研究主体
- B51
- 关联论文: ActivityDiff: a diffusion model with positive and negative activity guidance for de novo drug design | doi:; Apo2Mol: 3D Molecule Generation via Dynamic Pocket-Aware Diffusion Models | doi:; 3D Equivariant Diffusion for Target-Aware Molecule Generation and Affinity Prediction | doi:

## 本实例步骤描述
解析正负活性联合引导的靶向小分子生成的靶点、种子分子和生成任务。

## 本实例执行 prompt
读取{MOLECULE_INPUT}并检查化学结构，使用{MODEL_NAME}建立{GENERATION_MODE}模式的正负活性联合引导的靶向小分子生成任务。

## 本实例输入槽
- {MOLECULE_INPUT} | required=True | type=doc | var_name=分子设计输入 | hint=输入靶点或分子文件 | default=target_activity.csv
- {MODEL_NAME} | required=True | type=enum | var_name=分子模型 | hint=选择场景使用的模型 | default=TargetDiff
- {GENERATION_MODE} | required=False | type=enum | var_name=生成模式 | hint=选择分子生成任务 | default=de_novo

## 本实例产出
- 标准化分子输入
- 靶点条件
- 生成任务配置

## 本实例质量门禁
- 分子化学价合法
- 靶点条件可解析
- 生成模式与输入兼容

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
