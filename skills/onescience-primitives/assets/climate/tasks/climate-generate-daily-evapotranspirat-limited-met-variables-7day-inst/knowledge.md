# 实例任务：生成逐日蒸散发预报 @ E66

- domain: climate
- 骨架: climate-generate-daily-evapotranspiration-forecast-task
- 场景: climate-limited-met-variables-7day-ref-evapotranspiration-forecast-scenario (E66)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E66
- 关联论文: Hybrid Deep Learning for Week-Ahead Evapotranspiration Forecasting | doi:; Neural network approach to reference evapotranspiration modeling from limited climatic data in arid regions | doi:

## 本实例步骤描述
按冻结配置执行“生成逐日蒸散发预报”，完成从温度湿度风速辐射观测与预报到未来7天参考蒸散发序列的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{FORECAST_DAYS}、{OUTPUT_INTERVAL}执行生成逐日蒸散发预报，将温度湿度风速辐射观测与预报转换为未来7天参考蒸散发序列。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=蒸散发预报配置 | hint=输入蒸散发预报配置。 | default=None
- {FORECAST_DAYS} | required=True | type=str | var_name=预报天数 | hint=输入预报天数。 | default=7
- {OUTPUT_INTERVAL} | required=True | type=str | var_name=输出间隔 | hint=输入逐日输出间隔。 | default=1天

## 本实例产出
- 生成逐日蒸散发预报结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 水量、状态范围和洪峰时序不存在非物理异常
- 完整生成未来七个逐日参考蒸散发值

## 可调资源（edge:resource，仅真实存在）
- models/ensemble-model-output-statistics-emos-post-processing
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/wenhai-global-ocean-forecast-system

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
