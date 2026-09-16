# 实例任务：滚动预测干旱指数 @ E18

- domain: climate
- 骨架: climate-rolling-drought-index-forecast-task
- 场景: climate-basin-meteorological-drought-index-monthly-seasonal-scale-scenario (E18)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E18
- 关联论文: Short-term SPI drought forecasting in the Awash River Basin in Ethiopia using wavelet transforms and machine learning methods | doi:; Forecasting of meteorological drought using ensemble and machine learning models | doi:; Identification of influential weather parameters and seasonal drought prediction in Bangladesh using machine learning algorithm | doi:; Regional drought forecasting in data-scarce regions through a novel cluster-based liquid neural network | doi:

## 本实例步骤描述
按冻结配置执行“滚动预测干旱指数”，完成从历史气象序列、气候因子到SPI等干旱指数、等级与发生概率的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{INITIAL_STATE}、{ENSEMBLE_SIZE}执行滚动预测干旱指数，将历史气象序列、气候因子转换为SPI等干旱指数、等级与发生概率。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {INITIAL_STATE} | required=False | type=str | var_name=初始水文状态 | hint=输入初始水文状态路径。 | default=None
- {ENSEMBLE_SIZE} | required=True | type=str | var_name=集合成员数 | hint=输入集合成员数量。 | default=1

## 本实例产出
- 滚动预测干旱指数结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 水量、状态范围和洪峰时序不存在非物理异常

## 可调资源（edge:resource，仅真实存在）
- datasets/cesm2-large-ensemble
- datasets/large-ensemble-testbed
- models/crpsexp-loss-function-for-ensemble-forecasting
- models/ensemble-empirical-mode-decomposition-eemd
- models/ensemble-model-output-statistics-emos-post-processing

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
