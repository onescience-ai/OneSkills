# 骨架任务：模型与性质条件准备

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 加载权重并编码靶点、片段和优化性质。

## 执行 prompt（跨场景聚合去重）
- 加载{CHECKPOINT}，编码{OBJECTIVES}性质目标，并按{KEEP_SCAFFOLD}决定是否固定种子骨架。

## 输入槽（var/hint/default）
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=模型权重名称 | default=targetdiff.pt
- {OBJECTIVES} | required=False | type=list[str] | var_name=优化目标 | hint=列出需要优化的性质 | default=['QED', 'SA', 'affinity']
- {KEEP_SCAFFOLD} | required=False | type=bool | var_name=保留核心骨架 | hint=是否固定输入分子骨架 | default=False

## 产出
- 性质条件向量
- 模型加载记录
- 骨架约束

## 质量门禁 quality_gate
- 固定骨架原子映射有效
- 性质定义完整
- 权重版本可追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-0a68a065
- it-20278900
- it-3e4f83ce
- it-42c452e8
- it-45fbaf19
- it-4d2e327a
- it-5b23cb3d
- it-640e2608
- it-cf981af8
- it-fb90c673

## 复用场景
- B53
- B56
- B57
- B54
- B59
- B52
- B58
- B60
- B55
- B51
