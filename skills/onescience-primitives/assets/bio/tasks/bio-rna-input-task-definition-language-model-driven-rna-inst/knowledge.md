# 实例任务：RNA输入与任务定义 @ B81

- domain: bio
- 骨架: bio-rna-input-task-definition-task
- 场景: bio-language-model-driven-rna-3d-structure-prediction-scenario (B81)
- step_id: s01
- depend: []

## 场景研究主体
- B81
- 关联论文: Accurate RNA 3D structure prediction using a language model-based deep learning approach | doi:; BAnG: Bidirectional Anchored Generation for Conditional RNA Design | doi:

## 本实例步骤描述
读取语言模型驱动的RNA三维结构预测所需的RNA序列、结构或配对样本。

## 本实例执行 prompt
读取{RNA_INPUT}并检查碱基、链和配对标记，使用{MODEL_NAME}建立{TASK_MODE}模式的语言模型驱动的RNA三维结构预测任务。

## 本实例输入槽
- {RNA_INPUT} | required=True | type=doc | var_name=RNA输入 | hint=输入RNA序列或结构 | default=RNA_Puzzles.fasta
- {MODEL_NAME} | required=True | type=enum | var_name=RNA模型 | hint=选择场景使用的模型 | default=RhoFold
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
- models/alphafold
- tools/simplefold-protein-structure-prediction-model-and-pipeline

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
