# 骨架任务：预测目标站多时效浓度

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“预测目标站多时效浓度”，完成从目标与邻站PM2.5历史、站点位置、气象预报到逐时或逐日PM2.5浓度和超标概率的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{RUN_CONFIG}、{FORECAST_HORIZON}、{SPATIAL_GRID}执行预测目标站多时效浓度，将目标与邻站PM2.5历史、站点位置、气象预报转换为逐时或逐日PM2.5浓度和超标概率。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {FORECAST_HORIZON} | required=False | type=str | var_name=预测时效 | hint=输入目标预测时效。 | default=None
- {SPATIAL_GRID} | required=True | type=str | var_name=输出网格 | hint=输入输出网格规格。 | default=None

## 产出
- 中间状态与运行日志
- 资源和退出状态记录
- 预测目标站多时效浓度结果

## 质量门禁 quality_gate
- 核心计算未读取任务截止时间之后的数据
- 目标区域和时段内结果完整且无重复或错位
- 输出浓度或柱含量满足物理范围和掩膜约束
- 配置、随机种子、日志和中间状态能够追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-bf9adb73

## 复用场景
- E42
