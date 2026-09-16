# 实例任务：宏基因组输入与任务定义 @ B96

- domain: bio
- 骨架: bio-metagenome-input-task-definition-task
- 场景: bio-phage-lifestyle-classification-prediction-scenario (B96)
- step_id: s01
- depend: []

## 场景研究主体
- B96
- 关联论文: PhaTYP: Predicting the lifestyle for bacteriophages using BERT | doi:; PathoLM: Identifying pathogenicity from the DNA sequence through the Genome Foundation Model | doi:

## 本实例步骤描述
读取噬菌体生活方式分类预测所需的序列、丰度或宿主标签。

## 本实例执行 prompt
读取{METAGENOME_INPUT}中的{SEQUENCE_TYPE}序列并检查字符、长度和标签，使用{MODEL_NAME}建立噬菌体生活方式分类预测任务。

## 本实例输入槽
- {METAGENOME_INPUT} | required=True | type=doc | var_name=宏基因组输入 | hint=输入序列或特征表 | default=phage_contigs.fasta
- {MODEL_NAME} | required=True | type=enum | var_name=宏基因组模型 | hint=选择场景使用的模型 | default=PhaTYP
- {SEQUENCE_TYPE} | required=False | type=enum | var_name=序列类型 | hint=选择输入序列粒度 | default=contig

## 本实例产出
- 标准化序列
- 样本与标签表
- 任务配置

## 本实例质量门禁
- 序列字符合法
- 样本来源可追溯
- 标签定义无冲突

## 可调资源（edge:resource，仅真实存在）
- tools/simplefold-protein-structure-prediction-model-and-pipeline

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
