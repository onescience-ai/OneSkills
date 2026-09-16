# 实例任务：设计目标与约束定义 @ B16

- domain: bio
- 骨架: bio-design-objective-and-constraint-definition-task
- 场景: bio-substrate-pocket-constrained-enzyme-scaffold-design-scenario (B16)
- step_id: s01
- depend: []

## 场景研究主体
- B16
- 关联论文: EnzyPGM: Pocket-conditioned Generative Model for Substrate-specific Enzyme Design | doi:; Floating Anchor Diffusion Model for Multi-motif Scaffolding | doi:

## 本实例步骤描述
解析底物口袋约束的酶骨架设计的目标结构、功能条件和设计范围。

## 本实例执行 prompt
读取{DESIGN_INPUT}，使用{MODEL_NAME}定义长度为{TARGET_LENGTH}的底物口袋约束的酶骨架设计任务及可设计区域。

## 本实例输入槽
- {DESIGN_INPUT} | required=True | type=doc | var_name=设计输入 | hint=输入结构或约束文件 | default=substrate_pocket.sdf
- {MODEL_NAME} | required=True | type=enum | var_name=设计模型 | hint=选择场景使用的模型 | default=EnzyPGM
- {TARGET_LENGTH} | required=True | type=int | var_name=目标长度 | hint=设置目标残基数量 | default=256

## 本实例产出
- 标准化设计输入
- 约束清单
- 设计区域

## 本实例质量门禁
- 约束引用有效
- 目标长度受模型支持
- 设计区域无冲突

## 可调资源（edge:resource，仅真实存在）
- models/rdesign-tertiary-structure-based-rna-design
- tools/simplefold-protein-structure-prediction-model-and-pipeline

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
