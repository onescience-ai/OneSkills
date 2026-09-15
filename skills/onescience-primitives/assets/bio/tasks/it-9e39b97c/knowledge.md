# 实例任务：基因组预测或序列生成 @ B70

- domain: bio
- 骨架: tk-bio-641b5fc6
- 场景: sc-a42a7aa2 (B70)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- B70
- 关联论文: Dirichlet Flow Matching with Applications to DNA Sequence Design | doi:

## 本实例步骤描述
批量执行轨迹、分类、变异评分或条件生成。

## 本实例执行 prompt
以批次{BATCH_SIZE}和种子{SEED}运行单纯形流匹配的调控DNA序列设计，分别输出{CELL_CONTEXTS}上下文的结果。

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
- models/proteinmpnn

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
