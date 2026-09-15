# 实例任务：免疫对象与任务定义 @ B24

- domain: bio
- 骨架: tk-bio-6c6601c7
- 场景: sc-fa5646c7 (B24)
- step_id: s01
- depend: []

## 场景研究主体
- B24
- 关联论文: Fast and Accurate Antibody Sequence Design via Structure Retrieval | doi:; BetterBodies: Reinforcement Learning guided Diffusion for Antibody Sequence Design | doi:

## 本实例步骤描述
读取结构检索增强的抗体序列设计所需的抗原、抗体或受体数据。

## 本实例执行 prompt
校验{IMMUNE_INPUT}中的链、表位和标签，使用{MODEL_NAME}建立{TASK_MODE}模式的结构检索增强的抗体序列设计任务。

## 本实例输入槽
- {IMMUNE_INPUT} | required=True | type=doc | var_name=免疫输入数据 | hint=输入序列结构或配对表 | default=antibody_backbones.pdb
- {MODEL_NAME} | required=True | type=enum | var_name=免疫模型 | hint=选择场景使用的模型 | default=Antibody Retrieval Designer
- {TASK_MODE} | required=False | type=enum | var_name=任务模式 | hint=选择预测或设计任务 | default=design

## 本实例产出
- 标准化免疫数据
- 链与表位映射
- 任务配置

## 本实例质量门禁
- 链类型可识别
- 样本标识唯一
- 任务标签定义明确

## 可调资源（edge:resource，仅真实存在）
- models/proteinmpnn

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
