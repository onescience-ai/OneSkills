# 实例任务：结构约束与模型准备 @ B86

- domain: bio
- 骨架: tk-bio-97c29895
- 场景: sc-8c79aa2f (B86)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- B86
- 关联论文: Kirigami: large convolutional kernels improve deep learning-based RNA secondary structure prediction | doi:; gRNAde: Geometric Deep Learning for 3D RNA inverse design | doi:

## 本实例步骤描述
加载权重并编码二级、三级和固定序列约束。

## 本实例执行 prompt
加载{CHECKPOINT}，将序列限制在{MAX_LENGTH}以内，并按{ALLOW_PSEUDOKNOT}编码结构约束。

## 本实例输入槽
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=模型权重名称 | default=kirigami.pt
- {MAX_LENGTH} | required=False | type=int | var_name=RNA长度上限 | hint=限制RNA输入长度 | default=512
- {ALLOW_PSEUDOKNOT} | required=False | type=bool | var_name=允许假结 | hint=是否保留假结配对 | default=False

## 本实例产出
- RNA模型特征
- 结构约束
- 模型加载记录

## 本实例质量门禁
- 序列长度符合要求
- 结构约束可满足
- 固定碱基未丢失

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
