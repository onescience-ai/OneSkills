# 骨架任务：免疫对象与任务定义

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 读取CD4 T细胞表位加工与呈递预测所需的抗原、抗体或受体数据。
- 读取CDR环与抗体骨架联合生成所需的抗原、抗体或受体数据。
- 读取亲和力优化的结构感知抗体反向折叠所需的抗原、抗体或受体数据。
- 读取可解释TCR表位特异性预测所需的抗原、抗体或受体数据。
- 读取强化学习引导的抗体亲和力成熟所需的抗原、抗体或受体数据。
- 读取抗体抗原结合位点联合预测所需的抗原、抗体或受体数据。
- 读取抗原条件的全原子抗体从头设计所需的抗原、抗体或受体数据。
- 读取抗原特异性多模态抗体功能设计所需的抗原、抗体或受体数据。
- 读取新冠病毒抗体结合亲和力预测所需的抗原、抗体或受体数据。
- 读取结构检索增强的抗体序列设计所需的抗原、抗体或受体数据。

## 执行 prompt（跨场景聚合去重）
- 校验{IMMUNE_INPUT}中的链、表位和标签，使用{MODEL_NAME}建立{TASK_MODE}模式的CD4 T细胞表位加工与呈递预测任务。
- 校验{IMMUNE_INPUT}中的链、表位和标签，使用{MODEL_NAME}建立{TASK_MODE}模式的CDR环与抗体骨架联合生成任务。
- 校验{IMMUNE_INPUT}中的链、表位和标签，使用{MODEL_NAME}建立{TASK_MODE}模式的亲和力优化的结构感知抗体反向折叠任务。
- 校验{IMMUNE_INPUT}中的链、表位和标签，使用{MODEL_NAME}建立{TASK_MODE}模式的可解释TCR表位特异性预测任务。
- 校验{IMMUNE_INPUT}中的链、表位和标签，使用{MODEL_NAME}建立{TASK_MODE}模式的强化学习引导的抗体亲和力成熟任务。
- 校验{IMMUNE_INPUT}中的链、表位和标签，使用{MODEL_NAME}建立{TASK_MODE}模式的抗体抗原结合位点联合预测任务。
- 校验{IMMUNE_INPUT}中的链、表位和标签，使用{MODEL_NAME}建立{TASK_MODE}模式的抗原条件的全原子抗体从头设计任务。
- 校验{IMMUNE_INPUT}中的链、表位和标签，使用{MODEL_NAME}建立{TASK_MODE}模式的抗原特异性多模态抗体功能设计任务。
- 校验{IMMUNE_INPUT}中的链、表位和标签，使用{MODEL_NAME}建立{TASK_MODE}模式的新冠病毒抗体结合亲和力预测任务。
- 校验{IMMUNE_INPUT}中的链、表位和标签，使用{MODEL_NAME}建立{TASK_MODE}模式的结构检索增强的抗体序列设计任务。

## 输入槽（var/hint/default）
- {IMMUNE_INPUT} | required=True | type=doc | var_name=免疫输入数据 | hint=输入序列结构或配对表 | default=antibody_backbones.pdb
- {MODEL_NAME} | required=True | type=enum | var_name=免疫模型 | hint=选择场景使用的模型 | default=Antibody Retrieval Designer
- {TASK_MODE} | required=False | type=enum | var_name=任务模式 | hint=选择预测或设计任务 | default=design

## 产出
- 任务配置
- 标准化免疫数据
- 链与表位映射

## 质量门禁 quality_gate
- 任务标签定义明确
- 样本标识唯一
- 链类型可识别

## 可调资源（edge:resource，仅真实存在）
- models/proteinmpnn
- tools/simplefold-protein-structure-prediction-model-and-pipeline

## 实例任务（本骨架在各场景的实例化）
- bio-immune-target-task-definition-affinity-optimized-structure-inst
- bio-immune-target-task-definition-antibody-antigen-binding-inst
- bio-immune-target-task-definition-antigen-conditioned-full-inst
- bio-immune-target-task-definition-antigen-specific-multimodal-inst
- bio-immune-target-task-definition-cd4-t-cell-epitope-processin-inst
- bio-immune-target-task-definition-cdr-loop-antibody-scaffold-inst
- bio-immune-target-task-definition-interpretable-tcr-epitope-inst
- bio-immune-target-task-definition-reinforcement-learning-inst
- bio-immune-target-task-definition-sars-cov-2-antibody-binding-inst
- bio-immune-target-task-definition-structure-retrieval-augmente-inst

## 复用场景
- B26
- B22
- B28
- B27
- B23
- B25
- B21
- B30
- B29
- B24
