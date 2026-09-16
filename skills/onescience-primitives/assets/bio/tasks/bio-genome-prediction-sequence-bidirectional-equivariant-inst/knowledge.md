# 实例任务：基因组预测或序列生成 @ B64

- domain: bio
- 骨架: bio-genome-prediction-sequence-generation-task
- 场景: bio-bidirectional-equivariant-long-range-dna-sequence-modeling-scenario (B64)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- B64
- 关联论文: Caduceus: Bi-Directional Equivariant Long-Range DNA Sequence Modeling | doi:; DNABERT-2: Efficient Foundation Model and Benchmark For Multi-Species Genome | doi:

## 本实例步骤描述
批量执行轨迹、分类、变异评分或条件生成。

## 本实例执行 prompt
以批次{BATCH_SIZE}和种子{SEED}运行双向等变长程DNA序列建模，分别输出{CELL_CONTEXTS}上下文的结果。

## 本实例输入槽
- {BATCH_SIZE} | required=True | type=int | var_name=批次大小 | hint=设置序列批次大小 | default=8
- {CELL_CONTEXTS} | required=False | type=list[str] | var_name=细胞上下文 | hint=选择组织或细胞类型 | default=['K562', 'HepG2']
- {SEED} | required=False | type=int | var_name=随机种子 | hint=固定生成或评测结果 | default=2025

## 本实例产出
- 基因组预测
- 变异或生成分数
- 运行日志

## 本实例质量门禁
- 每个区间均有结果
- 正反链结果已对齐
- 数值无NaN或Inf

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
