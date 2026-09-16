# 实例任务：模型与条件特征准备 @ B18

- domain: bio
- 骨架: bio-model-condition-feature-preparation-task
- 场景: bio-multi-conformation-state-compatible-protein-sequence-design-scenario (B18)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- B18
- 关联论文: Multi-state Protein Design with DynamicMPNN | doi:

## 本实例步骤描述
加载权重并编码固定残基、对称性及功能条件。

## 本实例执行 prompt
加载{CHECKPOINT}，编码{FIXED_POSITIONS}固定残基与{SYMMETRY}对称条件，生成模型输入特征。

## 本实例输入槽
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=模型权重名称 | default=dynamicmpnn.pt
- {FIXED_POSITIONS} | required=False | type=list[int] | var_name=固定残基位点 | hint=列出保持不变的位点 | default=[10, 25]
- {SYMMETRY} | required=False | type=str | var_name=对称群 | hint=填写蛋白对称群 | default=C1

## 本实例产出
- 条件特征
- 固定残基掩码
- 模型加载记录

## 本实例质量门禁
- 固定位点在长度范围内
- 对称群可解析
- 条件特征无缺失

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
