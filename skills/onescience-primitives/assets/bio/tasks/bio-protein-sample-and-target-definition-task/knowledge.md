# 骨架任务：蛋白样本与目标定义

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 读取低样本多模态蛋白功能预测的序列、结构或变异样本及目标标签。
- 读取偏好优化驱动的蛋白功能注释的序列、结构或变异样本及目标标签。
- 读取多尺度表征的蛋白适应度预测的序列、结构或变异样本及目标标签。
- 读取残基层可解释的酶功能分类的序列、结构或变异样本及目标标签。
- 读取深度突变扫描监督的蛋白变异效应预测的序列、结构或变异样本及目标标签。
- 读取等变结构网络的突变稳定性预测的序列、结构或变异样本及目标标签。
- 读取蛋白突变效应解释与序列工程的序列、结构或变异样本及目标标签。
- 读取进化谱驱动的蛋白适应度预测的序列、结构或变异样本及目标标签。
- 读取酶分类与反应检索基准评测的序列、结构或变异样本及目标标签。
- 读取酶序列与底物联合的动力学常数预测的序列、结构或变异样本及目标标签。

## 执行 prompt（跨场景聚合去重）
- 解析{PROTEIN_DATA}并检查序列、变异和标签，使用{MODEL_NAME}建立{TARGET_TYPE}目标的低样本多模态蛋白功能预测任务。
- 解析{PROTEIN_DATA}并检查序列、变异和标签，使用{MODEL_NAME}建立{TARGET_TYPE}目标的偏好优化驱动的蛋白功能注释任务。
- 解析{PROTEIN_DATA}并检查序列、变异和标签，使用{MODEL_NAME}建立{TARGET_TYPE}目标的多尺度表征的蛋白适应度预测任务。
- 解析{PROTEIN_DATA}并检查序列、变异和标签，使用{MODEL_NAME}建立{TARGET_TYPE}目标的残基层可解释的酶功能分类任务。
- 解析{PROTEIN_DATA}并检查序列、变异和标签，使用{MODEL_NAME}建立{TARGET_TYPE}目标的深度突变扫描监督的蛋白变异效应预测任务。
- 解析{PROTEIN_DATA}并检查序列、变异和标签，使用{MODEL_NAME}建立{TARGET_TYPE}目标的等变结构网络的突变稳定性预测任务。
- 解析{PROTEIN_DATA}并检查序列、变异和标签，使用{MODEL_NAME}建立{TARGET_TYPE}目标的蛋白突变效应解释与序列工程任务。
- 解析{PROTEIN_DATA}并检查序列、变异和标签，使用{MODEL_NAME}建立{TARGET_TYPE}目标的进化谱驱动的蛋白适应度预测任务。
- 解析{PROTEIN_DATA}并检查序列、变异和标签，使用{MODEL_NAME}建立{TARGET_TYPE}目标的酶分类与反应检索基准评测任务。
- 解析{PROTEIN_DATA}并检查序列、变异和标签，使用{MODEL_NAME}建立{TARGET_TYPE}目标的酶序列与底物联合的动力学常数预测任务。

## 输入槽（var/hint/default）
- {PROTEIN_DATA} | required=True | type=doc | var_name=蛋白任务数据 | hint=输入序列结构或标签表 | default=enzyme_substrate.csv
- {MODEL_NAME} | required=True | type=enum | var_name=功能模型 | hint=选择场景使用的模型 | default=EnzyCLIP
- {TARGET_TYPE} | required=False | type=enum | var_name=预测目标 | hint=选择功能或效应目标 | default=continuous

## 产出
- 数据检查报告
- 标准化样本
- 标签字典

## 质量门禁 quality_gate
- 变异位点有效
- 序列字符合法
- 标签类型与目标一致

## 可调资源（edge:resource，仅真实存在）
- tools/alphafold-protein-structure-prediction-system
- tools/pdb-structure-data-access
- tools/simplefold-protein-structure-prediction-model-and-pipeline

## 实例任务（本骨架在各场景的实例化）
- bio-protein-sample-and-target-deep-mutational-scanning-inst
- bio-protein-sample-and-target-enzyme-classification-and-inst
- bio-protein-sample-and-target-enzyme-sequence-and-substrat-inst
- bio-protein-sample-and-target-equivariant-structural-inst
- bio-protein-sample-and-target-evolutionary-spectrum-inst
- bio-protein-sample-and-target-few-shot-multimodal-protein-inst
- bio-protein-sample-and-target-multi-scale-representation-inst
- bio-protein-sample-and-target-preference-optimization-inst
- bio-protein-sample-and-target-protein-mutation-effect-inst
- bio-protein-sample-and-target-residual-based-interpretable-inst

## 复用场景
- B39
- B32
- B38
- B37
- B31
- B34
- B35
- B36
- B40
- B33
