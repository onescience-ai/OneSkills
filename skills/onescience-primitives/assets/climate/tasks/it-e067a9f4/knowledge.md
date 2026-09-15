# 实例任务：天气暴露和目标观测及任务边界预检 @ E43

- domain: climate
- 骨架: tk-climate-85ec4115
- 场景: sc-7d1fa1a7 (E43)
- step_id: s01
- depend: []

## 场景研究主体
- E43
- 关联论文: Deep learning models for forecasting dengue fever based on climate data in Vietnam | doi:; Machine learning and dengue forecasting- Comparing random forests and artificial neural networks for predicting dengue burden at national and sub-national scales in Colombia | doi:; Machine learning methods reveal the temporal pattern of dengue incidence using meteorological factors in metropolitan Manila, Philippines | doi:

## 本实例步骤描述
界定“气象驱动的周尺度登革热发病量预报”的任务范围并执行“天气暴露和目标观测及任务边界预检”，核验气象历史与预报、病例序列、季节人口信息的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“气象驱动的周尺度登革热发病量预报”，读取{WEATHER_EXPOSURE}、{TARGET_OBSERVATIONS}、{CONTEXT_FEATURES}、{ANALYSIS_PERIOD}、{DATA_CUTOFF_TIME}并完成天气暴露和目标观测及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {WEATHER_EXPOSURE} | required=True | type=str | var_name=天气暴露资料 | hint=输入天气暴露资料路径。 | default=None
- {TARGET_OBSERVATIONS} | required=True | type=str | var_name=目标观测资料 | hint=输入目标观测资料路径。 | default=None
- {CONTEXT_FEATURES} | required=False | type=str | var_name=背景协变量 | hint=输入背景协变量路径。 | default=None
- {ANALYSIS_PERIOD} | required=True | type=str | var_name=分析预测时段 | hint=输入处理起止时间。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 天气、目标观测和背景协变量时空匹配

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
