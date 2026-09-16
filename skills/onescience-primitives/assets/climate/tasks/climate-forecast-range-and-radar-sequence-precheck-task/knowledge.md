# 骨架任务：起报范围与雷达序列预检

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 固定起报时间和预报时效，核验连续雷达历史序列的时间间隔、覆盖范围、变量、单位、缺测与资料截止时间。

## 执行 prompt（跨场景聚合去重）
- 读取{RADAR_HISTORY}，以{FORECAST_START_TIME}为起报时间，检查{HISTORY_FRAMES}帧、{FRAME_INTERVAL_MINUTES}分钟间隔和{DATA_CUTOFF_TIME}，并确认{FORECAST_HORIZON_MINUTES}不超过180分钟。报告覆盖、单位、缺帧、异常值和时间连续性；存在未来观测泄漏或关键帧缺失时停止并标记BLOCKED。

## 输入槽（var/hint/default）
- {RADAR_HISTORY} | required=True | type=str | var_name=连续雷达历史序列 | hint=输入连续雷达数据路径。 | default=None
- {FORECAST_START_TIME} | required=True | type=str | var_name=起报时间 | hint=输入UTC起报时间。 | default=None
- {HISTORY_FRAMES} | required=True | type=str | var_name=历史帧数 | hint=输入连续历史雷达帧数。 | default=9
- {FRAME_INTERVAL_MINUTES} | required=True | type=str | var_name=雷达帧间隔 | hint=输入帧间隔，单位分钟。 | default=10
- {FORECAST_HORIZON_MINUTES} | required=True | type=str | var_name=预报时长 | hint=输入预报时长，不超过180分钟。 | default=180
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 产出
- 历史帧时间轴与覆盖报告
- 雷达序列预检报告
- 雷达输入文件与资料截止时间清单

## 质量门禁 quality_gate
- 历史帧数量和时间间隔满足模型契约
- 所有输入雷达帧的有效时间均不晚于起报时间
- 缺帧、缺测区和异常回波已显式记录
- 雷达变量、单位、投影和覆盖范围均可识别

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

## 实例任务（本骨架在各场景的实例化）
- climate-forecast-range-and-radar-radar-driven-0-3-hour-inst

## 复用场景
- E2
