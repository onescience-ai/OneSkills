# 实例任务：RNA输入与任务定义 @ B85

- domain: bio
- 骨架: tk-bio-c3b69dac
- 场景: sc-32f26123 (B85)
- step_id: s01
- depend: []

## 场景研究主体
- B85
- 关联论文: gRNAde: Geometric Deep Learning for 3D RNA inverse design | doi:; Kirigami: large convolutional kernels improve deep learning-based RNA secondary structure prediction | doi:

## 本实例步骤描述
读取几何深度学习驱动的RNA三维反向设计所需的RNA序列、结构或配对样本。

## 本实例执行 prompt
读取{RNA_INPUT}并检查碱基、链和配对标记，使用{MODEL_NAME}建立{TASK_MODE}模式的几何深度学习驱动的RNA三维反向设计任务。

## 本实例输入槽
- {RNA_INPUT} | required=True | type=doc | var_name=RNA输入 | hint=输入RNA序列或结构 | default=rna_backbone.pdb
- {MODEL_NAME} | required=True | type=enum | var_name=RNA模型 | hint=选择场景使用的模型 | default=gRNAde
- {TASK_MODE} | required=False | type=enum | var_name=RNA任务模式 | hint=选择预测或设计模式 | default=prediction

## 本实例产出
- 标准化RNA输入
- 碱基与链映射
- 任务配置

## 本实例质量门禁
- 碱基字符合法
- 配对索引无冲突
- 模型与任务模式兼容

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
