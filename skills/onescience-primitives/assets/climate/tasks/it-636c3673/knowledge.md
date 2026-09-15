# 实例任务：起报资料及任务边界预检 @ E47

- domain: climate
- 骨架: tk-climate-b71baabb
- 场景: sc-43bddc37 (E47)
- step_id: s01
- depend: []

## 场景研究主体
- E47
- 关联论文: Skilful global seasonal predictions from a machine learning weather model trained on reanalysis data | doi:; Seasonal forecasting using the GenCast probabilistic machine learning model | doi:

## 本实例步骤描述
界定“全球1—6个月季节集合天气—气候预测”的任务范围并执行“起报资料及任务边界预检”，核验多个季节起报初态、边界状态、气候基准的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“全球1—6个月季节集合天气—气候预测”，读取{INITIAL_COUPLED_STATE}、{FORECAST_START_DATE}、{LEAD_MONTHS}、{TARGET_VARIABLES}、{DATA_CUTOFF_TIME}并完成起报资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {INITIAL_COUPLED_STATE} | required=True | type=str | var_name=大气海洋初态 | hint=输入大气海洋初态路径。 | default=None
- {FORECAST_START_DATE} | required=True | type=str | var_name=起报日期 | hint=输入UTC起报日期。 | default=None
- {LEAD_MONTHS} | required=True | type=str | var_name=月预见期 | hint=输入1至6月预见期。 | default=None
- {TARGET_VARIABLES} | required=True | type=str | var_name=目标变量与指数 | hint=输入变量和指数清单。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 所有动态输入的有效时间均不晚于资料截止时间
- 初始大气海洋状态和起报日对应同一业务时刻

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
