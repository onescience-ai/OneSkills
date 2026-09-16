# 实例任务：评测与解释汇总 @ B32

- domain: bio
- 骨架: bio-evaluation-and-interpretation-summary-task
- 场景: bio-preference-optimization-driven-protein-function-annotation-scenario (B32)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- B32
- 关联论文: AnnoDPO: Protein Functional Annotation Learning with Direct Preference Optimization | doi:; Fine-tuning Protein Language Models with Deep Mutational Scanning improves Variant Effect Prediction | doi:

## 本实例步骤描述
计算宏平均F1并输出残基、结构域或样本层解释。

## 本实例执行 prompt
计算宏平均F1并与{MIN_METRIC}比较，按{EXPORT_EXPLANATION}导出特征贡献和错误分析。

## 本实例输入槽
- {MIN_METRIC} | required=False | type=float | var_name=指标下限 | hint=设置合格指标下限 | default=0.6
- {EXPORT_EXPLANATION} | required=False | type=bool | var_name=导出解释 | hint=是否输出模型解释 | default=True

## 本实例产出
- 评测汇总
- 宏平均F1明细
- 解释与误差报告

## 本实例质量门禁
- 数据切分无泄漏
- 指标定义明确
- 解释可定位到原始样本

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
