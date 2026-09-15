# 实例任务：免疫对象与任务定义 @ B23

- domain: bio
- 骨架: tk-bio-6c6601c7
- 场景: sc-6ca6b41d (B23)
- step_id: s01
- depend: []

## 场景研究主体
- B23
- 关联论文: BetterBodies: Reinforcement Learning guided Diffusion for Antibody Sequence Design | doi:; Fast and Accurate Antibody Sequence Design via Structure Retrieval | doi:

## 本实例步骤描述
读取强化学习引导的抗体亲和力成熟所需的抗原、抗体或受体数据。

## 本实例执行 prompt
校验{IMMUNE_INPUT}中的链、表位和标签，使用{MODEL_NAME}建立{TASK_MODE}模式的强化学习引导的抗体亲和力成熟任务。

## 本实例输入槽
- {IMMUNE_INPUT} | required=True | type=doc | var_name=免疫输入数据 | hint=输入序列结构或配对表 | default=affinity_pairs.csv
- {MODEL_NAME} | required=True | type=enum | var_name=免疫模型 | hint=选择场景使用的模型 | default=BetterBodies
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
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
