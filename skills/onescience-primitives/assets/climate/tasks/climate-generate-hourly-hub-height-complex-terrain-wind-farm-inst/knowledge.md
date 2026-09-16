# 实例任务：生成逐时轮毂风场 @ E26

- domain: climate
- 骨架: climate-generate-hourly-hub-height-wind-field-task
- 场景: climate-complex-terrain-wind-farm-hub-height-short-term-wind-speed-scenario (E26)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E26
- 关联论文: A machine learning model for hub-height short-term wind speed prediction | doi:; Estimating hub-height wind speed based on a machine learning algorithm- implications for wind energy assessment | doi:; Terrain-aware Deep Learning for Wind Energy Applications- From Kilometer-scale Forecasts to Fine Wind Fields | doi:; The importance of round-robin validation when assessing machine-learning-based vertical extrapolation of wind speeds | doi:

## 本实例步骤描述
按冻结配置执行“生成逐时轮毂风场”，完成从近地面风、NWP、地形、轮毂高度到轮毂高度风速风向及误差范围的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{TARGET_HUB_HEIGHTS}、{OUTPUT_INTERVAL}执行生成逐时轮毂风场，将近地面风、NWP、地形、轮毂高度转换为轮毂高度风速风向及误差范围。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=轮毂风预报配置 | hint=输入轮毂风预报配置。 | default=None
- {TARGET_HUB_HEIGHTS} | required=True | type=str | var_name=目标轮毂高度 | hint=输入目标轮毂高度。 | default=None
- {OUTPUT_INTERVAL} | required=True | type=str | var_name=输出间隔 | hint=输入结果输出间隔。 | default=None

## 本实例产出
- 生成逐时轮毂风场结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 功率、负荷或辐照度输出满足物理边界
- 输出目标是轮毂高度风速且不转换为风电功率

## 可调资源（edge:resource，仅真实存在）
- datasets/gedi-footprint-canopy-height-data
- datasets/global-canopy-height-map-2020
- datasets/sgp-c1-multi-source-boundary-layer-height-dataset
- models/ensemble-model-output-statistics-emos-post-processing
- models/tucker-thresholding-method-for-boundary-layer-height-estimation

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
