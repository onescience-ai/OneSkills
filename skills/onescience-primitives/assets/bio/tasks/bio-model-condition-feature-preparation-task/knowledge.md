# 骨架任务：模型与条件特征准备

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 加载权重并编码固定残基、对称性及功能条件。

## 执行 prompt（跨场景聚合去重）
- 加载{CHECKPOINT}，编码{FIXED_POSITIONS}固定残基与{SYMMETRY}对称条件，生成模型输入特征。

## 输入槽（var/hint/default）
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=模型权重名称 | default=pepflow.ckpt
- {FIXED_POSITIONS} | required=False | type=list[int] | var_name=固定残基位点 | hint=列出保持不变的位点 | default=[10, 25]
- {SYMMETRY} | required=False | type=str | var_name=对称群 | hint=填写蛋白对称群 | default=C1

## 产出
- 固定残基掩码
- 条件特征
- 模型加载记录

## 质量门禁 quality_gate
- 固定位点在长度范围内
- 对称群可解析
- 条件特征无缺失

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- bio-model-condition-feature-all-atom-protein-structure-inst
- bio-model-condition-feature-functional-site-constrained-inst
- bio-model-condition-feature-given-protein-backbone-inst
- bio-model-condition-feature-multi-conformation-state-inst
- bio-model-condition-feature-multi-functional-motif-inst
- bio-model-condition-feature-protoken-latent-protein-inst
- bio-model-condition-feature-reaction-condition-driven-inst
- bio-model-condition-feature-substrate-pocket-constrained-inst
- bio-model-condition-feature-target-specific-all-atom-inst
- bio-model-condition-feature-transmembrane-protein-inst

## 复用场景
- B14
- B13
- B11
- B20
- B15
- B18
- B16
- B12
- B19
- B17
