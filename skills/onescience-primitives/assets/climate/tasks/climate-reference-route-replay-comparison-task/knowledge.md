# 骨架任务：与基准航线回放比较

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 执行“与基准航线回放比较”，使用未参与参数选择的参考资料检验优化航线、航时、能耗和风险，给出适用范围与交付判定。

## 执行 prompt（跨场景聚合去重）
- 依据{REPLAY_WEATHER}、{BASELINE_ROUTE}、{METRICS}、{ACCEPTANCE_CRITERIA}以独立参考资料完成与基准航线回放比较。按预先登记的区域、时段、事件或提前期计算指标并与同协议基线比较；缺少参考资料或验收门限时只能报告结果，不得声明性能PASS。

## 输入槽（var/hint/default）
- {REPLAY_WEATHER} | required=True | type=str | var_name=回放天气资料 | hint=输入独立回放天气路径。 | default=None
- {BASELINE_ROUTE} | required=True | type=str | var_name=基准航线 | hint=输入同航次基准航线。 | default=None
- {METRICS} | required=True | type=str | var_name=检验指标 | hint=输入航时油耗风险指标。 | default=None
- {ACCEPTANCE_CRITERIA} | required=False | type=str | var_name=验收门限 | hint=输入预先登记的门限。 | default=None

## 产出
- 分层检验指标报告
- 同协议基线比较报告
- 适用边界与交付判定

## 质量门禁 quality_gate
- 未达到预先登记门限时不得判定性能通过
- 结果与基线采用相同样本、网格和指标协议
- 航时、油耗、风险和约束违例与基准航线同协议比较
- 配置、日志、产物路径和文件哈希可追溯
- 验证资料未参与训练、参数选择或阈值调优

## 可调资源（edge:resource，仅真实存在）
- datasets/kling-gupta-efficiency-kge-metric
- datasets/precipitation-nowcasting-evaluation-metrics
- datasets/south-korea-air-quality-and-weather-monitoring-dataset
- tools/aardvark-weather-system
- tools/ai-global-medium-range-weather-forecasting-system-pangu-weather
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/fuxi-weather
- tools/gencast-global-probabilistic-weather-forecasting-model

## 实例任务（本骨架在各场景的实例化）
- climate-reference-route-replay-marine-weather-navigation-inst

## 复用场景
- E100
