# 骨架任务：结构约束与模型准备

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 加载权重并编码二级、三级和固定序列约束。

## 执行 prompt（跨场景聚合去重）
- 加载{CHECKPOINT}，将序列限制在{MAX_LENGTH}以内，并按{ALLOW_PSEUDOKNOT}编码结构约束。

## 输入槽（var/hint/default）
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=模型权重名称 | default=rhofold.pt
- {MAX_LENGTH} | required=False | type=int | var_name=RNA长度上限 | hint=限制RNA输入长度 | default=512
- {ALLOW_PSEUDOKNOT} | required=False | type=bool | var_name=允许假结 | hint=是否保留假结配对 | default=False

## 产出
- RNA模型特征
- 模型加载记录
- 结构约束

## 质量门禁 quality_gate
- 固定碱基未丢失
- 序列长度符合要求
- 结构约束可满足

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-2220128d
- it-373e4797
- it-4c2df879
- it-664ee1c5
- it-7fa7f48f
- it-833c18e5
- it-bba414d4
- it-bc975e51
- it-cd15e33b
- it-d8f09c20

## 复用场景
- B83
- B90
- B85
- B82
- B86
- B88
- B87
- B84
- B89
- B81
