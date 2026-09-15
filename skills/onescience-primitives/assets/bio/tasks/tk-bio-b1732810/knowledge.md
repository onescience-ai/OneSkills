# 骨架任务：序列过滤与模型准备

- domain: bio
- 复用场景数: 7
- 实例任务数: 7

## 步骤描述（跨场景聚合去重）
- 加载权重并进行长度过滤、分词和参考信息编码。

## 执行 prompt（跨场景聚合去重）
- 加载{CHECKPOINT}和{REFERENCE_DB}，过滤短于{MIN_CONTIG_LENGTH}的序列并生成模型特征。

## 输入槽（var/hint/default）
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=模型权重名称 | default=cross_species_amr.pt
- {MIN_CONTIG_LENGTH} | required=False | type=int | var_name=最短序列长度 | hint=设置最短序列碱基数 | default=1000
- {REFERENCE_DB} | required=False | type=doc | var_name=参考数据库 | hint=参考数据库名称 | default=GTDB_R220

## 产出
- 序列表征
- 过滤后序列
- 过滤统计

## 质量门禁 quality_gate
- 参考版本可追溯
- 序列与样本映射保持
- 过滤阈值已记录

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-181c6b58
- it-47035894
- it-6ccc4ad0
- it-8b010ed2
- it-950f8846
- it-d3a6b0d2
- it-e72fee01

## 复用场景
- B95
- B93
- B91
- B96
- B92
- B94
- B97
