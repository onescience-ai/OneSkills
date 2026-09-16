# 实例任务：RNA输入与任务定义 @ B90

- domain: bio
- 骨架: bio-rna-input-task-definition-task
- 场景: bio-low-data-rna-tertiary-structure-conditional-sequence-design-scenario (B90)
- step_id: s01
- depend: []

## 场景研究主体
- B90
- 关联论文: RDesign: Hierarchical Data-efficient Representation Learning for Tertiary Structure-based RNA Design | doi:

## 本实例步骤描述
读取低数据RNA三级结构条件序列设计所需的RNA序列、结构或配对样本。

## 本实例执行 prompt
读取{RNA_INPUT}并检查碱基、链和配对标记，使用{MODEL_NAME}建立{TASK_MODE}模式的低数据RNA三级结构条件序列设计任务。

## 本实例输入槽
- {RNA_INPUT} | required=True | type=doc | var_name=RNA输入 | hint=输入RNA序列或结构 | default=rna_tertiary.pdb
- {MODEL_NAME} | required=True | type=enum | var_name=RNA模型 | hint=选择场景使用的模型 | default=RDesign
- {TASK_MODE} | required=False | type=enum | var_name=RNA任务模式 | hint=选择预测或设计模式 | default=prediction

## 本实例产出
- 标准化RNA输入
- 碱基与链映射
- 任务配置

## 本实例质量门禁
- 碱基字符合法
- 配对索引无冲突
- 模型与任务模式兼容

## 可调资源（edge:resource，仅真实存在）
- models/proteinmpnn
- tools/simplefold-protein-structure-prediction-model-and-pipeline

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
