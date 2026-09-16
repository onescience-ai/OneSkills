# 骨架任务：重建三维温盐场并融合多尺度背景信息

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“重建三维温盐场并融合多尺度背景信息”，完成从稀疏温盐剖面、卫星表层观测和背景场到规则网格三维温盐分析场的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{CYCLE_CONFIG}、{FORECAST_HORIZON}、{CHECKPOINT_INTERVAL}执行重建三维温盐场并融合多尺度背景信息，将稀疏温盐剖面、卫星表层观测和背景场转换为规则网格三维温盐分析场。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {CYCLE_CONFIG} | required=True | type=str | var_name=循环配置 | hint=输入分析循环配置。 | default=None
- {FORECAST_HORIZON} | required=True | type=str | var_name=验证预报时效 | hint=输入验证预报时效。 | default=None
- {CHECKPOINT_INTERVAL} | required=True | type=str | var_name=中间保存间隔 | hint=输入中间状态保存间隔。 | default=None

## 产出
- 中间状态与运行日志
- 资源和退出状态记录
- 重建三维温盐场并融合多尺度背景信息结果

## 质量门禁 quality_gate
- 分析增量和循环状态不存在未解释的突变
- 核心计算未读取任务截止时间之后的数据
- 目标区域和时段内结果完整且无重复或错位
- 配置、随机种子、日志和中间状态能够追溯

## 可调资源（edge:resource，仅真实存在）
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/wenhai-global-ocean-forecast-system

## 实例任务（本骨架在各场景的实例化）
- climate-reconstruct-3d-temp-salinity-sparse-observation-3d-inst

## 复用场景
- E48
