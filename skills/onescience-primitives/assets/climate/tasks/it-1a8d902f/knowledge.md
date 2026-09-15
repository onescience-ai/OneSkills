# 实例任务：观测强迫样本及任务边界预检 @ E94

- domain: climate
- 骨架: tk-climate-dccb1776
- 场景: sc-c3edf438 (E94)
- step_id: s01
- depend: []

## 场景研究主体
- E94
- 关联论文: Anthropogenic fingerprints in daily precipitation revealed by deep learning | doi:

## 本实例步骤描述
界定“日降水场中的人为气候变化指纹检测”的任务范围并执行“观测强迫样本及任务边界预检”，核验气候模式大集合日降水、观测日降水的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“日降水场中的人为气候变化指纹检测”，读取{OBSERVED_DAILY_PRECIPITATION}、{FORCED_CLIMATE_SAMPLES}、{NATURAL_CLIMATE_SAMPLES}、{ANALYSIS_PERIOD}、{REFERENCE_PERIOD}并完成观测强迫样本及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {OBSERVED_DAILY_PRECIPITATION} | required=True | type=str | var_name=观测日降水场 | hint=输入观测日降水场路径。 | default=None
- {FORCED_CLIMATE_SAMPLES} | required=True | type=str | var_name=历史强迫样本 | hint=输入历史强迫样本路径。 | default=None
- {NATURAL_CLIMATE_SAMPLES} | required=True | type=str | var_name=自然强迫样本 | hint=输入自然强迫样本路径。 | default=None
- {ANALYSIS_PERIOD} | required=True | type=str | var_name=检测时段 | hint=输入指纹检测时段。 | default=None
- {REFERENCE_PERIOD} | required=True | type=str | var_name=参考基准期 | hint=输入参考基准时段。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 目标观测、驱动资料和参照样本定义可追溯
- 观测、历史强迫和自然强迫样本使用一致日降水定义

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
