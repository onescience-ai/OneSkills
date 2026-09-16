# 实例任务：结构约束与模型准备 @ B89

- domain: bio
- 骨架: bio-structure-constraint-and-model-preparation-task
- 场景: bio-protein-rna-complex-binding-affinity-prediction-scenario (B89)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- B89
- 关联论文: CoPRA: Bridging Cross-domain Pretrained Sequence Models with Complex Structures for Protein-RNA Binding Affinity Prediction | doi:

## 本实例步骤描述
加载权重并编码二级、三级和固定序列约束。

## 本实例执行 prompt
加载{CHECKPOINT}，将序列限制在{MAX_LENGTH}以内，并按{ALLOW_PSEUDOKNOT}编码结构约束。

## 本实例输入槽
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=模型权重名称 | default=copra.pt
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
