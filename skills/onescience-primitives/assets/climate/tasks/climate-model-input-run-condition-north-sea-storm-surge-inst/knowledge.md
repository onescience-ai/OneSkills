# 实例任务：模型输入与运行条件预检 @ E101

- domain: climate
- 骨架: climate-model-input-run-condition-precheck-task
- 场景: climate-north-sea-storm-surge-nowcast-model-scenario (E101)
- step_id: s01
- depend: []

## 场景研究主体
- E101
- 关联论文: 基于多变量LSTM神经网络模型的风暴潮临近预报 | doi:

## 本实例步骤描述
核对模型实际输入的数据身份、版本、权限、资料截止时间、变量、时空覆盖和缺测，形成输入清单与数据阻断项。

## 本实例执行 prompt
读取{SCHEDULED_SURGE_FORECAST}、{REALTIME_TIDE_DATA}和{REALTIME_WEATHER_DATA}，以{RUN_TIME}和{DATA_CUTOFF_TIME}核验北海区数据时效、300 m网格、接口延迟、缺测及未来资料泄漏。

## 本实例输入槽
- {SCHEDULED_SURGE_FORECAST} | required=True | type=str | var_name=定时风暴潮预报 | hint=输入已发布预报路径。 | default=None
- {REALTIME_TIDE_DATA} | required=True | type=str | var_name=实时逐小时潮位 | hint=输入实时潮位数据路径。 | default=None
- {REALTIME_WEATHER_DATA} | required=True | type=str | var_name=实时逐小时气象 | hint=输入实时气象数据路径。 | default=None
- {RUN_TIME} | required=True | type=str | var_name=模型运行时刻 | hint=输入本次运行UTC时间。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 本实例产出
- 输入数据与版本清单
- 输入时空变量与缺测检查报告
- 数据缺失、权限和契约阻断项

## 本实例质量门禁
- 输入文件存在、可读、获准使用且来源和版本可追溯
- 输入的区域、时段、网格、变量、单位、坐标和资料截止时间已逐项核对
- 未来资料、模型开发资料和独立验证资料的用途已隔离
- 输入数据中的缺失、冲突和异常未被推测值覆盖

## 可调资源（edge:resource，仅真实存在）
- datapipes/exploring-deep-learning-capabilities-surge-predictions-coastal
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/ostia-sst-data
- datasets/snodas-swe-data-product
- datasets/south-korea-air-quality-and-weather-monitoring-dataset
- models/dynamic-pre-training-for-time-series-dynpt
- models/multivariate-data-fusion-vector-wind-prediction
- tools/aardvark-weather-system
- tools/ai-global-medium-range-weather-forecasting-system-pangu-weather
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/fuxi-weather
- tools/gencast-global-probabilistic-weather-forecasting-model
- tools/wenhai-global-ocean-forecast-system

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
