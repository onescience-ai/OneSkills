# 实例任务：输入与任务定义 @ B01

- domain: bio
- 骨架: bio-input-and-task-definition-task
- 场景: bio-protein-monomer-structure-prediction-and-confidence-assessment-scenario (B01)
- step_id: s01
- depend: []

## 场景研究主体
- B01
- 关联论文: Highly accurate protein structure prediction with AlphaFold | doi:; Quantifying the Role of OpenFold Components in Protein Structure Prediction | doi:

## 本实例步骤描述
校验蛋白质单体结构预测与置信度评估所需的序列、链组成和任务设置。

## 本实例执行 prompt
读取{INPUT_DATA}，检查实体、序列和链标识，使用{MODEL_NAME}并按{CHAIN_MODE}建立蛋白质单体结构预测与置信度评估任务。

## 本实例输入槽
- {INPUT_DATA} | required=True | type=doc | var_name=序列或结构输入 | hint=输入FASTA或结构文件 | default=6kwc.fasta
- {MODEL_NAME} | required=True | type=enum | var_name=结构模型 | hint=选择场景使用的模型 | default=AlphaFold
- {CHAIN_MODE} | required=False | type=enum | var_name=链处理模式 | hint=指定单链或多链处理 | default=auto

## 本实例产出
- 标准化输入
- 实体清单
- 任务配置

## 本实例质量门禁
- 输入可被解析
- 链标识唯一
- 模型支持输入实体

## 可调资源（edge:resource，仅真实存在）
- models/alphafold
- tools/pdb-structure-data-access
- tools/simplefold-protein-structure-prediction-model-and-pipeline

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
