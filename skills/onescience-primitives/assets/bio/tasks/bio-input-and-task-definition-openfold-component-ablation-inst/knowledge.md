# 实例任务：输入与任务定义 @ B02

- domain: bio
- 骨架: bio-input-and-task-definition-task
- 场景: bio-openfold-component-ablation-structural-generalization-scenario (B02)
- step_id: s01
- depend: []

## 场景研究主体
- B02
- 关联论文: Quantifying the Role of OpenFold Components in Protein Structure Prediction | doi:; Highly accurate protein structure prediction with AlphaFold | doi:; OpenFold: Retraining AlphaFold2 yields new insights into its learning mechanisms and capacity for generalization | doi:

## 本实例步骤描述
校验OpenFold组件消融与结构泛化评测所需的序列、链组成和任务设置。

## 本实例执行 prompt
读取{INPUT_DATA}，按来源记录把序列映射到靶标、实体和链，再使用{MODEL_NAME}判定与{CHAIN_MODE}是否兼容。FASTA 每条记录是一条序列，不代表一个独立单链靶标；多链输入须有来源支持的链及实体组合。 对可核对的原链标识、残基编号和插入码保留到规范化输入的映射，不能从 FASTA 中推定缺失的结构编号。

## 本实例输入槽
- {INPUT_DATA} | required=True | type=doc | var_name=序列或结构输入 | hint=输入FASTA或结构文件 | default=CAMEO_targets.fasta
- {MODEL_NAME} | required=True | type=enum | var_name=结构模型 | hint=选择场景使用的模型 | default=OpenFold
- {CHAIN_MODE} | required=False | type=enum | var_name=链处理模式 | hint=指定单链或多链处理 | default=auto

## 本实例产出
- 标准化输入
- 实体清单：靶标、实体和链的对应关系，以及序列和原残基编号的映射；下游步骤沿用该映射。
- 任务配置

## 本实例质量门禁
- 输入可被解析
- 链标识唯一
- 模型支持输入实体

## 可调资源（edge:resource，仅真实存在）
- models/openfold
- tools/pdb-structure-data-access
- tools/simplefold-protein-structure-prediction-model-and-pipeline

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
