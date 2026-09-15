# 实例任务：水文强迫和流域资料及任务边界预检 @ E82

- domain: climate
- 骨架: tk-climate-14a78ebe
- 场景: sc-d8efa0d0 (E82)
- step_id: s01
- depend: []

## 场景研究主体
- E82
- 关联论文: A Committee Evolutionary Neural Network for the Prediction of Combined Sewer Overflows | doi:

## 本实例步骤描述
界定“降雨与管网状态驱动的合流制溢流事件预报”的任务范围并执行“水文强迫和流域资料及任务边界预检”，核验降雨预报、管网水位流量、泵闸运行的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“降雨与管网状态驱动的合流制溢流事件预报”，读取{METEOROLOGICAL_FORCING}、{BASIN_ATTRIBUTES}、{HYDROLOGICAL_OBSERVATIONS}、{SIMULATION_PERIOD}、{DATA_CUTOFF_TIME}并完成水文强迫和流域资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {METEOROLOGICAL_FORCING} | required=True | type=str | var_name=气象强迫资料 | hint=输入气象强迫资料路径。 | default=None
- {BASIN_ATTRIBUTES} | required=True | type=str | var_name=流域属性资料 | hint=输入流域属性资料路径。 | default=None
- {HYDROLOGICAL_OBSERVATIONS} | required=False | type=str | var_name=水文观测资料 | hint=输入水文观测资料路径。 | default=None
- {SIMULATION_PERIOD} | required=True | type=str | var_name=模拟预报时段 | hint=输入处理起止时间。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 气象强迫、流域边界和水文观测时空一致

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
