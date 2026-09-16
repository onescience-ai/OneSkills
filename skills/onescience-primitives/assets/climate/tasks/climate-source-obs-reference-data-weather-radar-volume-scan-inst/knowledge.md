# 实例任务：源观测和参考资料及任务边界预检 @ E34

- domain: climate
- 骨架: climate-source-obs-reference-data-boundary-task
- 场景: climate-weather-radar-volume-scan-driven-realtime-quantitative-scenario (E34)
- step_id: s01
- depend: []

## 场景研究主体
- E34
- 关联论文: A Deep Learning Approach to Radar‐Based QPE | doi:; Integration of shapley additive explanations with random forest model for quantitative precipitation estimation of mesoscale convective systems | doi:; RainForest- a random forest algorithm for quantitative precipitation estimation over Switzerland | doi:

## 本实例步骤描述
界定“天气雷达体扫驱动的实时定量降水估计”的任务范围并执行“源观测和参考资料及任务边界预检”，核验雷达多仰角反射率、雨量计观测、质量标识的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“天气雷达体扫驱动的实时定量降水估计”，读取{RADAR_VOLUME}、{RAIN_GAUGE_DATA}、{RADAR_SCAN_TIME}、{TARGET_REGION}、{DATA_CUTOFF_TIME}并完成源观测和参考资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {RADAR_VOLUME} | required=True | type=str | var_name=雷达体扫资料 | hint=输入雷达体扫资料路径。 | default=None
- {RAIN_GAUGE_DATA} | required=True | type=str | var_name=雨量计校准资料 | hint=输入雨量计校准资料。 | default=None
- {RADAR_SCAN_TIME} | required=True | type=str | var_name=雷达扫描时刻 | hint=输入雷达扫描时刻。 | default=None
- {TARGET_REGION} | required=True | type=str | var_name=目标区域 | hint=输入目标区域范围。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 源观测与辅助资料的有效时间和来源可追溯
- 输入限定为雷达体扫和雨量计校准资料且不要求卫星资料

## 可调资源（edge:resource，仅真实存在）
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/ostia-sst-data
- datasets/snodas-swe-data-product
- datasets/uk-radar-composite-dataset
- models/dynamic-pre-training-for-time-series-dynpt
- models/multivariate-data-fusion-vector-wind-prediction

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
