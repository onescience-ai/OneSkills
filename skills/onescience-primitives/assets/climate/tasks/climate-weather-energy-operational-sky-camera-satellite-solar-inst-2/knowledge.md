# 实例任务：天气能源运行资料时空对齐与样本构造 @ E23

- domain: climate
- 骨架: climate-weather-energy-operational-data-space-time-alignment-task
- 场景: climate-sky-camera-satellite-solar-irradiance-nowcast-scenario (E23)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- E23
- 关联论文: A Deep Learning Approach to Solar-Irradiance Forecasting in Sky-Videos | doi:; IrradianceNet- Spatiotemporal deep learning model for satellite-derived solar irradiance short-term forecasting | doi:; Sky Imager-Based Forecast of Solar Irradiance Using Machine Learning | doi:; A regional solar forecasting approach using generative adversarial networks with solar irradiance maps | doi:

## 本实例步骤描述
执行“天气能源运行资料时空对齐与样本构造”，统一天空图像、卫星云图、历史辐照度的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 本实例执行 prompt
依据{IMAGE_CALIBRATION_CONFIG}、{TIME_ALIGNMENT_CONFIG}、{CLEAR_SKY_CONFIG}完成天气能源运行资料时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 本实例输入槽
- {IMAGE_CALIBRATION_CONFIG} | required=True | type=str | var_name=影像定标配置 | hint=输入影像定标配置。 | default=None
- {TIME_ALIGNMENT_CONFIG} | required=True | type=str | var_name=时间对齐配置 | hint=输入图像辐照度对齐配置。 | default=None
- {CLEAR_SKY_CONFIG} | required=True | type=str | var_name=晴空基准配置 | hint=输入晴空基准配置。 | default=None

## 本实例产出
- 对齐后的标准输入
- 掩膜与样本索引
- 预处理转换记录

## 本实例质量门禁
- 预处理后的时间轴、坐标、单位和形状可检查
- 每项插值、归一化、掩膜和缺测处理均有记录
- 不存在由验证资料或未来资料造成的信息泄漏
- 容量、时区、采样间隔和缺测规则一致

## 可调资源（edge:resource，仅真实存在）
- models/dynamic-pre-training-for-time-series-dynpt
- models/neural-network-based-nwp-model-calibration

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
