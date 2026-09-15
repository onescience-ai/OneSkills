# 实例任务：预测目标站多时效浓度 @ E42

- domain: climate
- 骨架: tk-climate-0f0ba114
- 场景: sc-56496e0c (E42)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E42
- 关联论文: An improved deep learning model for predicting daily PM2.5 concentration | doi:; Dynamically pre-trained deep recurrent neural networks using environmental monitoring data for predicting PM2.5 | doi:; PM2.5 forecasting for an urban area based on deep learning and decomposition method | doi:

## 本实例步骤描述
按冻结配置执行“预测目标站多时效浓度”，完成从目标与邻站PM2.5历史、站点位置、气象预报到逐时或逐日PM2.5浓度和超标概率的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{FORECAST_HORIZON}、{SPATIAL_GRID}执行预测目标站多时效浓度，将目标与邻站PM2.5历史、站点位置、气象预报转换为逐时或逐日PM2.5浓度和超标概率。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {FORECAST_HORIZON} | required=False | type=str | var_name=预测时效 | hint=输入目标预测时效。 | default=None
- {SPATIAL_GRID} | required=True | type=str | var_name=输出网格 | hint=输入输出网格规格。 | default=None

## 本实例产出
- 预测目标站多时效浓度结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 输出浓度或柱含量满足物理范围和掩膜约束

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
