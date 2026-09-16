# 实例任务：模型输入与运行条件预检 @ E102

- domain: climate
- 骨架: climate-model-input-run-condition-precheck-task
- 场景: climate-north-sea-storm-surge-intelligent-correction-scenario (E102)
- step_id: s01
- depend: []

## 场景研究主体
- E102
- 关联论文: 基于机器学习的广东海域模式风暴潮数据订正及评估 | doi:; 基于深度学习的潮位预报订正技术研究 | doi:; 长短期记忆神经网络（LSTM）对风暴潮数值模拟的优化应用 | doi:

## 本实例步骤描述
核对模型实际输入的数据身份、版本、权限、资料截止时间、变量、时空覆盖和缺测，形成输入清单与数据阻断项。

## 本实例执行 prompt
读取{STORM_SURGE_FORECAST}、{METEOROLOGICAL_FIELDS}、{PREVIOUS_DAY_SIMULATION}和{SURGE_OBSERVATIONS}，以{DATA_CUTOFF_TIME}核验北海区数据身份、300 m网格、起报、有效时刻、站点和未来资料泄漏。

## 本实例输入槽
- {STORM_SURGE_FORECAST} | required=True | type=str | var_name=风暴潮数值预报 | hint=输入当天网格预报路径。 | default=None
- {METEOROLOGICAL_FIELDS} | required=True | type=str | var_name=气象场 | hint=输入气象驱动场路径。 | default=None
- {PREVIOUS_DAY_SIMULATION} | required=True | type=str | var_name=前日模拟结果 | hint=输入前一天模拟路径。 | default=None
- {SURGE_OBSERVATIONS} | required=True | type=str | var_name=风暴潮观测数据 | hint=输入可用观测数据路径。 | default=None
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
- datasets/lpma-airport-wind-observation-validation
- datasets/manila-dengue-meteorological-dataset
- datasets/ostia-sst-data
- datasets/snodas-swe-data-product
- models/anomaly-numerical-correction-with-observations-ano
- models/dynamic-pre-training-for-time-series-dynpt
- models/multivariate-data-fusion-vector-wind-prediction
- models/random-forest-meteorological-normalization
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/urban-hydrological-hydraulic-model-chain-for-inundation-simulation
- tools/wenhai-global-ocean-forecast-system

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
