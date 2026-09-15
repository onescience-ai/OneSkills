# 骨架任务：结构质控与汇总

- domain: bio
- 复用场景数: 10
- 实例任务数: 10

## 步骤描述（跨场景聚合去重）
- 按DockQ及几何完整性筛选并汇总结果。
- 按GDT-TS及几何完整性筛选并汇总结果。
- 按JS散度及几何完整性筛选并汇总结果。
- 按Pearson相关及几何完整性筛选并汇总结果。
- 按TM-score及几何完整性筛选并汇总结果。
- 按ipTM及几何完整性筛选并汇总结果。
- 按pLDDT及几何完整性筛选并汇总结果。
- 按构象覆盖率及几何完整性筛选并汇总结果。

## 执行 prompt（跨场景聚合去重）
- 计算DockQ，用{QUALITY_THRESHOLD}标记低质量候选，并按{OUTPUT_FORMAT}导出排序结构。
- 计算GDT-TS，用{QUALITY_THRESHOLD}标记低质量候选，并按{OUTPUT_FORMAT}导出排序结构。
- 计算JS散度，用{QUALITY_THRESHOLD}标记低质量候选，并按{OUTPUT_FORMAT}导出排序结构。
- 计算Pearson相关，用{QUALITY_THRESHOLD}标记低质量候选，并按{OUTPUT_FORMAT}导出排序结构。
- 计算TM-score，用{QUALITY_THRESHOLD}标记低质量候选，并按{OUTPUT_FORMAT}导出排序结构。
- 计算ipTM，用{QUALITY_THRESHOLD}标记低质量候选，并按{OUTPUT_FORMAT}导出排序结构。
- 计算pLDDT，用{QUALITY_THRESHOLD}标记低质量候选，并按{OUTPUT_FORMAT}导出排序结构。
- 计算构象覆盖率，用{QUALITY_THRESHOLD}标记低质量候选，并按{OUTPUT_FORMAT}导出排序结构。

## 输入槽（var/hint/default）
- {QUALITY_THRESHOLD} | required=False | type=float | var_name=质量阈值 | hint=设置候选质量下限 | default=0.7
- {OUTPUT_FORMAT} | required=False | type=enum | var_name=结构格式 | hint=选择结构输出格式 | default=mmCIF

## 产出
- DockQ汇总表
- GDT-TS汇总表
- JS散度汇总表
- Pearson相关汇总表
- TM-score汇总表
- ipTM汇总表
- pLDDT汇总表
- 排序结构
- 构象覆盖率汇总表
- 结构质控报告

## 质量门禁 quality_gate
- 低质量候选已标记
- 结构文件可解析
- 结果可追溯到参数

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-0da4e943
- it-401dc9dc
- it-555ee0c0
- it-802db04b
- it-81d447f3
- it-a3ece62f
- it-b7565e3f
- it-c6be4074
- it-d8d9e268
- it-e539c1b0

## 复用场景
- B02
- B08
- B03
- B10
- B01
- B09
- B07
- B04
- B05
- B06
