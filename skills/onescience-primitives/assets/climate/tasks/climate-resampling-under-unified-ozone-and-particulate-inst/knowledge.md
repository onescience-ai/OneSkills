# 实例任务：在统一气象分布下重采样预测 @ E45

- domain: climate
- 骨架: climate-resampling-under-unified-meteorological-distribution-task
- 场景: climate-ozone-and-particulate-matter-historical-series-meteorological-scenario (E45)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E45
- 关联论文: A machine learning approach to quantify meteorological drivers of ozone pollution in China from 2015 to 2019 | doi:; Assessing the impact of clean air action on air quality trends in Beijing using a machine learning technique | doi:; Meteorology-driven variability of air pollution (PM1) revealed with explainable machine learning | doi:

## 本实例步骤描述
按冻结配置执行“在统一气象分布下重采样预测”，完成从历史污染观测、同期气象和时间特征到气象归一化浓度、趋势分解和特征贡献的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{NORMALIZATION_CONFIG}、{RESAMPLING_COUNT}、{TREND_CONFIG}执行在统一气象分布下重采样预测，将历史污染观测、同期气象和时间特征转换为气象归一化浓度、趋势分解和特征贡献。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {NORMALIZATION_CONFIG} | required=True | type=str | var_name=气象归一化配置 | hint=输入气象归一化配置。 | default=None
- {RESAMPLING_COUNT} | required=True | type=str | var_name=重采样次数 | hint=输入重采样次数。 | default=1000
- {TREND_CONFIG} | required=True | type=str | var_name=趋势估计配置 | hint=输入趋势估计配置。 | default=None

## 本实例产出
- 在统一气象分布下重采样预测结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 检测、关联和因果归因结论被明确区分
- 重采样到统一气象分布后再估计去气象化趋势

## 可调资源（edge:resource，仅真实存在）
- models/importance-sampling-strategy-for-extreme-events
- models/random-forest-meteorological-normalization

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
