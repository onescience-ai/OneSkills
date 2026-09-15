# 实例任务：结构质控与汇总 @ B02

- domain: bio
- 骨架: tk-bio-f2a9ed46
- 场景: sc-36dea452 (B02)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- B02
- 关联论文: Quantifying the Role of OpenFold Components in Protein Structure Prediction | doi:; Highly accurate protein structure prediction with AlphaFold | doi:; OpenFold: Retraining AlphaFold2 yields new insights into its learning mechanisms and capacity for generalization | doi:

## 本实例步骤描述
按TM-score及几何完整性筛选并汇总结果。

## 本实例执行 prompt
计算TM-score，用{QUALITY_THRESHOLD}标记低质量候选，并按{OUTPUT_FORMAT}导出排序结构。

## 本实例输入槽
- {QUALITY_THRESHOLD} | required=False | type=float | var_name=质量阈值 | hint=设置候选质量下限 | default=0.7
- {OUTPUT_FORMAT} | required=False | type=enum | var_name=结构格式 | hint=选择结构输出格式 | default=mmCIF

## 本实例产出
- 排序结构
- TM-score汇总表
- 结构质控报告

## 本实例质量门禁
- 结构文件可解析
- 低质量候选已标记
- 结果可追溯到参数

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
