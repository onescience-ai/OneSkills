# 实例任务：设计目标与约束定义 @ B13

- domain: bio
- 骨架: tk-bio-d3c81df0
- 场景: sc-783047a7 (B13)
- step_id: s01
- depend: []

## 场景研究主体
- B13
- 关联论文: La-Proteina: Atomistic Protein Generation via Partially Latent Flow Matching | doi:; Consistent Synthetic Sequences Unlock Structural Diversity in Fully Atomistic De Novo Protein Design | doi:

## 本实例步骤描述
解析全原子蛋白结构与序列联合生成的目标结构、功能条件和设计范围。

## 本实例执行 prompt
读取{DESIGN_INPUT}，使用{MODEL_NAME}定义长度为{TARGET_LENGTH}的全原子蛋白结构与序列联合生成任务及可设计区域。

## 本实例输入槽
- {DESIGN_INPUT} | required=True | type=doc | var_name=设计输入 | hint=输入结构或约束文件 | default=protein_lengths.csv
- {MODEL_NAME} | required=True | type=enum | var_name=设计模型 | hint=选择场景使用的模型 | default=La-Proteina
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
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
