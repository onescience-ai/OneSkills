# 实例任务：滚动生成流量过程 @ E6

- domain: climate
- 骨架: tk-climate-3b282671
- 场景: sc-2b699093 (E6)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E6
- 关联论文: Enhancing Streamflow Forecast and Extracting Insights Using Long‐Short Term Memory Networks With Data Integration at Continental Scales | doi:; Neural networks and non-parametric methods for improving real-time flood forecasting through conceptual hydrological models | doi:; River Flow Forecasting with Artificial Neural Networks Using Satellite-Observed Precipitation Pre-Processed with Flow Length and Travel Time Information | doi:; Using a long short-term memory (LSTM) neural network to boost river streamflow forecasts over the western United States | doi:

## 本实例步骤描述
按冻结配置执行“滚动生成流量过程”，完成从实时雨量流量、流域状态、未来气象预报到多时效流量、洪峰与峰时的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{INITIAL_STATE}、{ENSEMBLE_SIZE}执行滚动生成流量过程，将实时雨量流量、流域状态、未来气象预报转换为多时效流量、洪峰与峰时。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {INITIAL_STATE} | required=False | type=str | var_name=初始水文状态 | hint=输入初始水文状态路径。 | default=None
- {ENSEMBLE_SIZE} | required=True | type=str | var_name=集合成员数 | hint=输入集合成员数量。 | default=1

## 本实例产出
- 滚动生成流量过程结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 水量、状态范围和洪峰时序不存在非物理异常

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
