# 实例任务：分子设计目标定义 @ B55

- domain: bio
- 骨架: bio-molecular-design-objective-definition-task
- 场景: bio-shape-electrostatic-pharmacophore-bioisostere-design-scenario (B55)
- step_id: s01
- depend: []

## 场景研究主体
- B55
- 关联论文: ShEPhERD: Diffusing shape, electrostatics, and pharmacophores for bioisosteric drug design | doi:; SMILES-Mamba: Chemical Mamba Foundation Models for Drug ADMET Prediction | doi:

## 本实例步骤描述
解析形状静电药效团联合的生物电子等排体设计的靶点、种子分子和生成任务。

## 本实例执行 prompt
读取{MOLECULE_INPUT}并检查化学结构，使用{MODEL_NAME}建立{GENERATION_MODE}模式的形状静电药效团联合的生物电子等排体设计任务。

## 本实例输入槽
- {MOLECULE_INPUT} | required=True | type=doc | var_name=分子设计输入 | hint=输入靶点或分子文件 | default=reference_ligand.sdf
- {MODEL_NAME} | required=True | type=enum | var_name=分子模型 | hint=选择场景使用的模型 | default=ShEPhERD
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
