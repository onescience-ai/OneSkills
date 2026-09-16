# 实例任务：生物一致性与泛化评估 @ B77

- domain: bio
- 骨架: bio-biological-consistency-and-generalization-evaluation-task
- 场景: bio-single-cell-to-spatial-transcriptome-missing-expression-recovery-scenario (B77)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- B77
- 关联论文: CASPER: Cross-modal Alignment of Spatial and single-cell Profiles for Expression Recovery | doi:

## 本实例步骤描述
计算基因相关性并检查细胞类型、通路和空间结构保持。

## 本实例执行 prompt
基于{LABEL_KEY}和{MIN_CORRELATION}评估基因相关性、差异表达及结构保持并汇总失败条件。

## 本实例输入槽
- {MIN_CORRELATION} | required=False | type=float | var_name=相关性下限 | hint=设置表达相关性下限 | default=0.5
- {LABEL_KEY} | required=False | type=str | var_name=评测标签字段 | hint=填写真实标签列名 | default=cell_type

## 本实例产出
- 评测结果
- 基因相关性明细
- 生物一致性报告

## 本实例质量门禁
- 训练测试样本隔离
- 低质量细胞已标记
- 结果保留原始细胞索引

## 可调资源（edge:resource，仅真实存在）
- tools/pydeseq2

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
