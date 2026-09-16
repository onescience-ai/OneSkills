# 骨架任务：RNA输入与任务定义

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 读取RNA三维靶结构的群智能反向折叠所需的RNA序列、结构或配对样本。
- 读取低数据RNA三级结构条件序列设计所需的RNA序列、结构或配对样本。
- 读取几何深度学习驱动的RNA三维反向设计所需的RNA序列、结构或配对样本。
- 读取双向锚定的结构条件RNA序列生成所需的RNA序列、结构或配对样本。
- 读取大卷积核RNA二级结构预测所需的RNA序列、结构或配对样本。
- 读取深度序列模型的miRNA靶标预测所需的RNA序列、结构或配对样本。
- 读取线性时间RNA二级结构折叠预测所需的RNA序列、结构或配对样本。
- 读取结构序列编码多约束的RNA设计所需的RNA序列、结构或配对样本。
- 读取蛋白质RNA复合物结合亲和力预测所需的RNA序列、结构或配对样本。
- 读取语言模型驱动的RNA三维结构预测所需的RNA序列、结构或配对样本。

## 执行 prompt（跨场景聚合去重）
- 读取{RNA_INPUT}并检查碱基、链和配对标记，使用{MODEL_NAME}建立{TASK_MODE}模式的RNA三维靶结构的群智能反向折叠任务。
- 读取{RNA_INPUT}并检查碱基、链和配对标记，使用{MODEL_NAME}建立{TASK_MODE}模式的低数据RNA三级结构条件序列设计任务。
- 读取{RNA_INPUT}并检查碱基、链和配对标记，使用{MODEL_NAME}建立{TASK_MODE}模式的几何深度学习驱动的RNA三维反向设计任务。
- 读取{RNA_INPUT}并检查碱基、链和配对标记，使用{MODEL_NAME}建立{TASK_MODE}模式的双向锚定的结构条件RNA序列生成任务。
- 读取{RNA_INPUT}并检查碱基、链和配对标记，使用{MODEL_NAME}建立{TASK_MODE}模式的大卷积核RNA二级结构预测任务。
- 读取{RNA_INPUT}并检查碱基、链和配对标记，使用{MODEL_NAME}建立{TASK_MODE}模式的深度序列模型的miRNA靶标预测任务。
- 读取{RNA_INPUT}并检查碱基、链和配对标记，使用{MODEL_NAME}建立{TASK_MODE}模式的线性时间RNA二级结构折叠预测任务。
- 读取{RNA_INPUT}并检查碱基、链和配对标记，使用{MODEL_NAME}建立{TASK_MODE}模式的结构序列编码多约束的RNA设计任务。
- 读取{RNA_INPUT}并检查碱基、链和配对标记，使用{MODEL_NAME}建立{TASK_MODE}模式的蛋白质RNA复合物结合亲和力预测任务。
- 读取{RNA_INPUT}并检查碱基、链和配对标记，使用{MODEL_NAME}建立{TASK_MODE}模式的语言模型驱动的RNA三维结构预测任务。

## 输入槽（var/hint/default）
- {RNA_INPUT} | required=True | type=doc | var_name=RNA输入 | hint=输入RNA序列或结构 | default=RNA_Puzzles.fasta
- {MODEL_NAME} | required=True | type=enum | var_name=RNA模型 | hint=选择场景使用的模型 | default=RhoFold
- {TASK_MODE} | required=False | type=enum | var_name=RNA任务模式 | hint=选择预测或设计模式 | default=prediction

## 产出
- 任务配置
- 标准化RNA输入
- 碱基与链映射

## 质量门禁 quality_gate
- 模型与任务模式兼容
- 碱基字符合法
- 配对索引无冲突

## 可调资源（edge:resource，仅真实存在）
- models/alphafold
- models/proteinmpnn
- tools/simplefold-protein-structure-prediction-model-and-pipeline

## 实例任务（本骨架在各场景的实例化）
- bio-rna-input-task-definition-bidirectional-anchored-inst
- bio-rna-input-task-definition-deep-sequence-model-mirna-inst
- bio-rna-input-task-definition-geometric-deep-learning-inst
- bio-rna-input-task-definition-language-model-driven-rna-inst
- bio-rna-input-task-definition-large-kernel-rna-secondary-inst
- bio-rna-input-task-definition-linear-time-rna-secondary-inst
- bio-rna-input-task-definition-low-data-rna-tertiary-inst
- bio-rna-input-task-definition-protein-rna-complex-binding-inst
- bio-rna-input-task-definition-rna-3d-target-structure-inst
- bio-rna-input-task-definition-structure-sequence-encoded-inst

## 复用场景
- B83
- B90
- B85
- B82
- B86
- B88
- B87
- B84
- B89
- B81
