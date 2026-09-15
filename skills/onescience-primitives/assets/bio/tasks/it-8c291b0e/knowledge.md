# 实例任务：生态与分类质量评估 @ B93

- domain: bio
- 骨架: tk-bio-0299abd1
- 场景: sc-d32093c7 (B93)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- B93
- 关联论文: FGBERT: Function-Driven Pre-trained Gene Language Model for Metagenomics | doi:; METAGENE-1: Metagenomic Foundation Model for Pandemic Monitoring | doi:

## 本实例步骤描述
计算宏平均F1并检查跨物种、样本和数据集泛化。

## 本实例执行 prompt
计算宏平均F1，按{MIN_CONFIDENCE}标记可信结果，并依据{REPORT_UNKNOWN}保留未知类别。

## 本实例输入槽
- {MIN_CONFIDENCE} | required=False | type=float | var_name=置信度下限 | hint=设置报告置信度下限 | default=0.7
- {REPORT_UNKNOWN} | required=False | type=bool | var_name=报告未知类别 | hint=是否保留未知类别结果 | default=True

## 本实例产出
- 评测汇总
- 宏平均F1明细
- 未知与异常清单

## 本实例质量门禁
- 评测按样本隔离
- 未知类别未被静默丢弃
- 结果可回溯原序列

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
