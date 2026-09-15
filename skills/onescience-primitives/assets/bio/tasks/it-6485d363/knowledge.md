# 实例任务：RNA结构与功能质控 @ B90

- domain: bio
- 骨架: tk-bio-94e026f3
- 场景: sc-dffda14d (B90)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- B90
- 关联论文: RDesign: Hierarchical Data-efficient Representation Learning for Tertiary Structure-based RNA Design | doi:

## 本实例步骤描述
计算序列恢复率并检查结构一致性、序列约束和候选多样性。

## 本实例执行 prompt
计算序列恢复率，用{SCORE_THRESHOLD}筛选候选，并按{OUTPUT_FORMAT}导出结构、序列和质控结果。

## 本实例输入槽
- {SCORE_THRESHOLD} | required=False | type=float | var_name=结果阈值 | hint=设置合格结果阈值 | default=0.6
- {OUTPUT_FORMAT} | required=False | type=enum | var_name=输出格式 | hint=选择RNA结果格式 | default=dot_bracket

## 本实例产出
- 排序候选
- 序列恢复率汇总
- RNA质控报告

## 本实例质量门禁
- 结构格式可解析
- 硬约束全部满足
- 低质量候选已标记

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
