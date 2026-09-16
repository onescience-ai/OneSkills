# 实例任务：蛋白样本与目标定义 @ B36

- domain: bio
- 骨架: bio-protein-sample-and-target-definition-task
- 场景: bio-evolutionary-spectrum-driven-protein-fitness-prediction-scenario (B36)
- step_id: s01
- depend: []

## 场景研究主体
- B36
- 关联论文: Evolutionary Profiles for Protein Fitness Prediction | doi:; MutaPLM: Protein Language Modeling for Mutation Explanation and Engineering | doi:

## 本实例步骤描述
读取进化谱驱动的蛋白适应度预测的序列、结构或变异样本及目标标签。

## 本实例执行 prompt
解析{PROTEIN_DATA}并检查序列、变异和标签，使用{MODEL_NAME}建立{TARGET_TYPE}目标的进化谱驱动的蛋白适应度预测任务。

## 本实例输入槽
- {PROTEIN_DATA} | required=True | type=doc | var_name=蛋白任务数据 | hint=输入序列结构或标签表 | default=homolog_alignment.a3m
- {MODEL_NAME} | required=True | type=enum | var_name=功能模型 | hint=选择场景使用的模型 | default=Evolutionary Profile Model
- {TARGET_TYPE} | required=False | type=enum | var_name=预测目标 | hint=选择功能或效应目标 | default=continuous

## 本实例产出
- 标准化样本
- 标签字典
- 数据检查报告

## 本实例质量门禁
- 序列字符合法
- 变异位点有效
- 标签类型与目标一致

## 可调资源（edge:resource，仅真实存在）
- tools/alphafold-protein-structure-prediction-system
- tools/pdb-structure-data-access
- tools/simplefold-protein-structure-prediction-model-and-pipeline

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
