# 实例任务：序列过滤与模型准备 @ B93

- domain: bio
- 骨架: bio-sequence-filtering-model-preparation-task
- 场景: bio-function-guided-metageneome-gene-characterization-and-scenario (B93)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- B93
- 关联论文: FGBERT: Function-Driven Pre-trained Gene Language Model for Metagenomics | doi:; METAGENE-1: Metagenomic Foundation Model for Pandemic Monitoring | doi:

## 本实例步骤描述
加载权重并进行长度过滤、分词和参考信息编码。

## 本实例执行 prompt
加载{CHECKPOINT}和{REFERENCE_DB}，过滤短于{MIN_CONTIG_LENGTH}的序列并生成模型特征。

## 本实例输入槽
- {CHECKPOINT} | required=True | type=doc | var_name=模型权重 | hint=模型权重名称 | default=fgbert.pt
- {MIN_CONTIG_LENGTH} | required=False | type=int | var_name=最短序列长度 | hint=设置最短序列碱基数 | default=1000
- {REFERENCE_DB} | required=False | type=doc | var_name=参考数据库 | hint=参考数据库名称 | default=GTDB_R220

## 本实例产出
- 过滤后序列
- 序列表征
- 过滤统计

## 本实例质量门禁
- 过滤阈值已记录
- 参考版本可追溯
- 序列与样本映射保持

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
