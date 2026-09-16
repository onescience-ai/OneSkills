# 骨架任务：编号与界面特征准备

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 加载权重并构建CDR、表位和界面条件特征。

## 执行 prompt（跨场景聚合去重）
- 加载{CHECKPOINT}，对{CDR_REGIONS}编号并限制单段长度为{MAX_CDR_LENGTH}，构建界面特征。

## 输入槽（var/hint/default）
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=模型权重名称 | default=retrieval_ab.pt
- {CDR_REGIONS} | required=False | type=list[str] | var_name=设计CDR区域 | hint=选择参与任务的CDR | default=['H1', 'H2', 'H3']
- {MAX_CDR_LENGTH} | required=False | type=int | var_name=CDR长度上限 | hint=限制单段CDR长度 | default=30

## 产出
- CDR掩码
- 抗原界面特征
- 标准抗体编号

## 质量门禁 quality_gate
- CDR编号连续
- 抗原抗体链映射正确
- 长度不超限

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- bio-numbering-and-interface-affinity-optimized-structure-inst
- bio-numbering-and-interface-antibody-antigen-binding-inst
- bio-numbering-and-interface-antigen-conditioned-full-inst
- bio-numbering-and-interface-antigen-specific-multimodal-inst
- bio-numbering-and-interface-cd4-t-cell-epitope-processin-inst
- bio-numbering-and-interface-cdr-loop-antibody-scaffold-inst
- bio-numbering-and-interface-interpretable-tcr-epitope-inst
- bio-numbering-and-interface-reinforcement-learning-inst
- bio-numbering-and-interface-sars-cov-2-antibody-binding-inst
- bio-numbering-and-interface-structure-retrieval-augmente-inst

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
