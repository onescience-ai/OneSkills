# 骨架任务：序列窗口与模型准备

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 加载权重并构造满足上下文长度的正反链输入。

## 执行 prompt（跨场景聚合去重）
- 加载{CHECKPOINT}，按{CONTEXT_LENGTH}构造序列窗口，并按{REVERSE_COMPLEMENT}生成方向增强特征。

## 输入槽（var/hint/default）
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=模型权重名称 | default=alphagenome_weights
- {CONTEXT_LENGTH} | required=False | type=int | var_name=上下文长度 | hint=设置DNA窗口碱基数 | default=131072
- {REVERSE_COMPLEMENT} | required=False | type=bool | var_name=反向互补增强 | hint=是否加入反向互补序列 | default=True

## 产出
- 序列窗口
- 方向映射
- 模型加载记录

## 质量门禁 quality_gate
- 中心坐标未偏移
- 反向映射可恢复
- 窗口长度符合模型要求

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- bio-sequence-window-model-bidirectional-equivariant-inst
- bio-sequence-window-model-cell-type-specific-regulator-inst
- bio-sequence-window-model-dna-language-model-biologica-inst
- bio-sequence-window-model-genomic-language-model-inst
- bio-sequence-window-model-histone-modification-driven-inst
- bio-sequence-window-model-long-dna-interval-multi-inst
- bio-sequence-window-model-million-base-context-genome-inst
- bio-sequence-window-model-multi-species-dna-sequence-inst
- bio-sequence-window-model-rice-breeding-variant-inst
- bio-sequence-window-model-simplex-flow-matching-inst

## 复用场景
- B65
- B70
- B64
- B66
- B63
- B69
- B62
- B68
- B67
- B61
