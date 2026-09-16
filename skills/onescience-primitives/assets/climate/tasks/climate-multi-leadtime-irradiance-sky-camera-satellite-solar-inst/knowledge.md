# 实例任务：生成多时效辐照度 @ E23

- domain: climate
- 骨架: climate-multi-leadtime-irradiance-task
- 场景: climate-sky-camera-satellite-solar-irradiance-nowcast-scenario (E23)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E23
- 关联论文: A Deep Learning Approach to Solar-Irradiance Forecasting in Sky-Videos | doi:; IrradianceNet- Spatiotemporal deep learning model for satellite-derived solar irradiance short-term forecasting | doi:; Sky Imager-Based Forecast of Solar Irradiance Using Machine Learning | doi:; A regional solar forecasting approach using generative adversarial networks with solar irradiance maps | doi:

## 本实例步骤描述
按冻结配置执行“生成多时效辐照度”，完成从天空图像、卫星云图、历史辐照度到多时效辐照度场或站点序列的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{LEAD_TIMES}、{OUTPUT_INTERVAL}执行生成多时效辐照度，将天空图像、卫星云图、历史辐照度转换为多时效辐照度场或站点序列。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=辐照度预报配置 | hint=输入辐照度预报配置。 | default=None
- {LEAD_TIMES} | required=True | type=str | var_name=目标提前期 | hint=输入目标提前期清单。 | default=None
- {OUTPUT_INTERVAL} | required=True | type=str | var_name=输出间隔 | hint=输入结果输出间隔。 | default=None

## 本实例产出
- 生成多时效辐照度结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 功率、负荷或辐照度输出满足物理边界
- 每个分钟至小时提前期均生成辐照度而非光伏功率

## 可调资源（edge:resource，仅真实存在）
- models/dynamic-pre-training-for-time-series-dynpt
- models/ensemble-model-output-statistics-emos-post-processing

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
