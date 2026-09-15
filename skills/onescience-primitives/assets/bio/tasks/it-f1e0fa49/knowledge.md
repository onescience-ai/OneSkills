# 实例任务：编号与界面特征准备 @ B25

- domain: bio
- 骨架: tk-bio-5070a32d
- 场景: sc-1f440561 (B25)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- B25
- 关联论文: CAME-AB: Cross-Modality Attention with Mixture-of-Experts for Antibody Binding Site Prediction | doi:; APLSuite: An Integrated Suite for CD4+ T Cell Epitope Prediction via Antigen Processing Likelihood | doi:

## 本实例步骤描述
加载权重并构建CDR、表位和界面条件特征。

## 本实例执行 prompt
加载{CHECKPOINT}，对{CDR_REGIONS}编号并限制单段长度为{MAX_CDR_LENGTH}，构建界面特征。

## 本实例输入槽
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=模型权重名称 | default=came_ab.pt
- {CDR_REGIONS} | required=False | type=list[str] | var_name=设计CDR区域 | hint=选择参与任务的CDR | default=['H1', 'H2', 'H3']
- {MAX_CDR_LENGTH} | required=False | type=int | var_name=CDR长度上限 | hint=限制单段CDR长度 | default=30

## 本实例产出
- 标准抗体编号
- CDR掩码
- 抗原界面特征

## 本实例质量门禁
- CDR编号连续
- 长度不超限
- 抗原抗体链映射正确

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
