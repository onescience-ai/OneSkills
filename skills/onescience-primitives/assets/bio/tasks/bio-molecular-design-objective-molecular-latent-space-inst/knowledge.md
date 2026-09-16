# 实例任务：分子设计目标定义 @ B52

- domain: bio
- 骨架: bio-molecular-design-objective-definition-task
- 场景: bio-molecular-latent-space-diffusion-evolution-and-multi-site-scenario (B52)
- step_id: s01
- depend: []

## 场景研究主体
- B52
- 关联论文: Apo2Mol: 3D Molecule Generation via Dynamic Pocket-Aware Diffusion Models | doi:; ActivityDiff: a diffusion model with positive and negative activity guidance for de novo drug design | doi:; MolSculptor: a diffusion-evolution framework for multi-site inhibitor design | doi:

## 本实例步骤描述
解析分子潜空间扩散进化与多位点抑制剂设计的靶点、种子分子和生成任务。

## 本实例执行 prompt
读取{MOLECULE_INPUT}并检查化学结构，使用{MODEL_NAME}建立{GENERATION_MODE}模式的分子潜空间扩散进化与多位点抑制剂设计任务。

## 本实例输入槽
- {MOLECULE_INPUT} | required=True | type=doc | var_name=分子设计输入 | hint=输入靶点或分子文件 | default=PI3K_targets.json
- {MODEL_NAME} | required=True | type=enum | var_name=分子模型 | hint=选择场景使用的模型 | default=MolSculptor
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
- tools/simplefold-protein-structure-prediction-model-and-pipeline

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
