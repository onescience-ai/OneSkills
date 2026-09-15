# 实例任务：蛋白样本与目标定义 @ B34

- domain: bio
- 骨架: tk-bio-f74cea1d
- 场景: sc-ceecec72 (B34)
- step_id: s01
- depend: []

## 场景研究主体
- B34
- 关联论文: HERMES: Holographic Equivariant neuRal network model for Mutational Effect and Stability prediction | doi:; EnzyCLIP: A Cross-Attention Dual Encoder Framework with Contrastive Learning for Predicting Enzyme Kinetic Constants | doi:

## 本实例步骤描述
读取等变结构网络的突变稳定性预测的序列、结构或变异样本及目标标签。

## 本实例执行 prompt
解析{PROTEIN_DATA}并检查序列、变异和标签，使用{MODEL_NAME}建立{TARGET_TYPE}目标的等变结构网络的突变稳定性预测任务。

## 本实例输入槽
- {PROTEIN_DATA} | required=True | type=doc | var_name=蛋白任务数据 | hint=输入序列结构或标签表 | default=stability_mutations.csv
- {MODEL_NAME} | required=True | type=enum | var_name=功能模型 | hint=选择场景使用的模型 | default=HERMES
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
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
