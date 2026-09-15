# 骨架任务：宏基因组输入与任务定义

- domain: bio
- 复用场景数: 7
- 实例任务数: 7

## 步骤描述（跨场景聚合去重）
- 读取DNA序列驱动的微生物致病性识别所需的序列、丰度或宿主标签。
- 读取功能引导的宏基因组基因表征与分类所需的序列、丰度或宿主标签。
- 读取噬菌体与原核宿主互作预测所需的序列、丰度或宿主标签。
- 读取噬菌体生活方式分类预测所需的序列、丰度或宿主标签。
- 读取对比学习驱动的宏基因组分箱所需的序列、丰度或宿主标签。
- 读取病原监测宏基因组基础模型所需的序列、丰度或宿主标签。
- 读取跨物种抗菌药物耐药性预测所需的序列、丰度或宿主标签。

## 执行 prompt（跨场景聚合去重）
- 读取{METAGENOME_INPUT}中的{SEQUENCE_TYPE}序列并检查字符、长度和标签，使用{MODEL_NAME}建立DNA序列驱动的微生物致病性识别任务。
- 读取{METAGENOME_INPUT}中的{SEQUENCE_TYPE}序列并检查字符、长度和标签，使用{MODEL_NAME}建立功能引导的宏基因组基因表征与分类任务。
- 读取{METAGENOME_INPUT}中的{SEQUENCE_TYPE}序列并检查字符、长度和标签，使用{MODEL_NAME}建立噬菌体与原核宿主互作预测任务。
- 读取{METAGENOME_INPUT}中的{SEQUENCE_TYPE}序列并检查字符、长度和标签，使用{MODEL_NAME}建立噬菌体生活方式分类预测任务。
- 读取{METAGENOME_INPUT}中的{SEQUENCE_TYPE}序列并检查字符、长度和标签，使用{MODEL_NAME}建立对比学习驱动的宏基因组分箱任务。
- 读取{METAGENOME_INPUT}中的{SEQUENCE_TYPE}序列并检查字符、长度和标签，使用{MODEL_NAME}建立病原监测宏基因组基础模型任务。
- 读取{METAGENOME_INPUT}中的{SEQUENCE_TYPE}序列并检查字符、长度和标签，使用{MODEL_NAME}建立跨物种抗菌药物耐药性预测任务。

## 输入槽（var/hint/default）
- {METAGENOME_INPUT} | required=True | type=doc | var_name=宏基因组输入 | hint=输入序列或特征表 | default=amr_genomes.fasta
- {MODEL_NAME} | required=True | type=enum | var_name=宏基因组模型 | hint=选择场景使用的模型 | default=Cross-Species Genomic Foundation Model
- {SEQUENCE_TYPE} | required=False | type=enum | var_name=序列类型 | hint=选择输入序列粒度 | default=contig

## 产出
- 任务配置
- 标准化序列
- 样本与标签表

## 质量门禁 quality_gate
- 序列字符合法
- 标签定义无冲突
- 样本来源可追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-25bfaee2
- it-3a39b64d
- it-69d6eb48
- it-8d955438
- it-bca3e3a1
- it-e0ea66c4
- it-ea05c289

## 复用场景
- B95
- B93
- B91
- B96
- B92
- B94
- B97
