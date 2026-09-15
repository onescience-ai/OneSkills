# 实例任务：回折叠与设计筛选 @ B11

- domain: bio
- 骨架: tk-bio-bae1be11
- 场景: sc-18c8a2d3 (B11)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- B11
- 关联论文: De novo design of protein structure and function with RFdiffusion | doi:; Robust deep learning-based protein sequence design using ProteinMPNN | doi:

## 本实例步骤描述
按基序RMSD、结构自洽性和约束满足度筛选候选。

## 本实例执行 prompt
计算基序RMSD并以{METRIC_THRESHOLD}筛选；按{KEEP_DIVERSE}控制去冗余后导出候选。

## 本实例输入槽
- {METRIC_THRESHOLD} | required=False | type=float | var_name=筛选阈值 | hint=设置核心指标下限 | default=0.6
- {KEEP_DIVERSE} | required=False | type=bool | var_name=保留多样候选 | hint=是否执行序列去冗余 | default=True

## 本实例产出
- 入选设计
- 基序RMSD汇总表
- 约束质控报告

## 本实例质量门禁
- 入选设计满足硬约束
- 结构几何无严重冲突
- 序列多样性已报告

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
