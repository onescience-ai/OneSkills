# 实例任务：起报范围与雷达序列预检 @ E2

- domain: climate
- 骨架: climate-forecast-range-and-radar-sequence-precheck-task
- 场景: climate-radar-driven-0-3-hour-extreme-precipitation-ensemble-nowcasting-scenario (E2)
- step_id: s01
- depend: []

## 场景研究主体
- E2
- 关联论文: Skilful nowcasting of extreme precipitation with NowcastNet | doi:; Skilful precipitation nowcasting using deep generative models of radar | doi:; Convolutional LSTM Network: A Machine Learning Approach for Precipitation Nowcasting | doi:; RainNet v1.0: a convolutional neural network for radar-based precipitation nowcasting | doi:

## 本实例步骤描述
固定起报时间和预报时效，核验连续雷达历史序列的时间间隔、覆盖范围、变量、单位、缺测与资料截止时间。

## 本实例执行 prompt
读取{RADAR_HISTORY}，以{FORECAST_START_TIME}为起报时间，检查{HISTORY_FRAMES}帧、{FRAME_INTERVAL_MINUTES}分钟间隔和{DATA_CUTOFF_TIME}，并确认{FORECAST_HORIZON_MINUTES}不超过180分钟。报告覆盖、单位、缺帧、异常值和时间连续性；存在未来观测泄漏或关键帧缺失时停止并标记BLOCKED。

## 本实例输入槽
- {RADAR_HISTORY} | required=True | type=str | var_name=连续雷达历史序列 | hint=输入连续雷达数据路径。 | default=None
- {FORECAST_START_TIME} | required=True | type=str | var_name=起报时间 | hint=输入UTC起报时间。 | default=None
- {HISTORY_FRAMES} | required=True | type=str | var_name=历史帧数 | hint=输入连续历史雷达帧数。 | default=9
- {FRAME_INTERVAL_MINUTES} | required=True | type=str | var_name=雷达帧间隔 | hint=输入帧间隔，单位分钟。 | default=10
- {FORECAST_HORIZON_MINUTES} | required=True | type=str | var_name=预报时长 | hint=输入预报时长，不超过180分钟。 | default=180
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 本实例产出
- 雷达输入文件与资料截止时间清单
- 历史帧时间轴与覆盖报告
- 雷达序列预检报告

## 本实例质量门禁
- 所有输入雷达帧的有效时间均不晚于起报时间
- 历史帧数量和时间间隔满足模型契约
- 雷达变量、单位、投影和覆盖范围均可识别
- 缺帧、缺测区和异常回波已显式记录

## 可调资源（edge:resource，仅真实存在）
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/ostia-sst-data
- datasets/snodas-swe-data-product
- datasets/uk-radar-composite-dataset
- models/dynamic-pre-training-for-time-series-dynpt
- models/multivariate-data-fusion-vector-wind-prediction
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/wenhai-global-ocean-forecast-system

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
