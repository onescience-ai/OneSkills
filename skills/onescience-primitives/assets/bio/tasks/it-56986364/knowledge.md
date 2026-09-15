# 实例任务：特异性与可开发性质控 @ B22

- domain: bio
- 骨架: tk-bio-78af6937
- 场景: sc-a813f314 (B22)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- B22
- 关联论文: AbODE: Ab Initio Antibody Design using Conjoined ODEs | doi:; AbFlow: End-to-end Paratope-Centric Antibody Design by Interaction Enhanced Flow Matching | doi:

## 本实例步骤描述
按CDR-RMSD及序列、结构和特异性指标筛选结果。

## 本实例执行 prompt
计算CDR-RMSD和可开发性指标，用{SCORE_THRESHOLD}筛选并保留前{TOP_K}个候选。

## 本实例输入槽
- {SCORE_THRESHOLD} | required=False | type=float | var_name=得分阈值 | hint=设置候选得分下限 | default=0.7
- {TOP_K} | required=False | type=int | var_name=保留数量 | hint=设置最终保留数量 | default=20

## 本实例产出
- 排序候选
- CDR-RMSD结果
- 可开发性报告

## 本实例质量门禁
- 关键CDR未异常截断
- 低特异候选已标记
- 保留规则可复现

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
