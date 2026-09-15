# 骨架任务：在统一气象分布下重采样预测

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“在统一气象分布下重采样预测”，完成从历史污染观测、同期气象和时间特征到气象归一化浓度、趋势分解和特征贡献的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{NORMALIZATION_CONFIG}、{RESAMPLING_COUNT}、{TREND_CONFIG}执行在统一气象分布下重采样预测，将历史污染观测、同期气象和时间特征转换为气象归一化浓度、趋势分解和特征贡献。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {NORMALIZATION_CONFIG} | required=True | type=str | var_name=气象归一化配置 | hint=输入气象归一化配置。 | default=None
- {RESAMPLING_COUNT} | required=True | type=str | var_name=重采样次数 | hint=输入重采样次数。 | default=1000
- {TREND_CONFIG} | required=True | type=str | var_name=趋势估计配置 | hint=输入趋势估计配置。 | default=None

## 产出
- 中间状态与运行日志
- 在统一气象分布下重采样预测结果
- 资源和退出状态记录

## 质量门禁 quality_gate
- 核心计算未读取任务截止时间之后的数据
- 检测、关联和因果归因结论被明确区分
- 目标区域和时段内结果完整且无重复或错位
- 配置、随机种子、日志和中间状态能够追溯
- 重采样到统一气象分布后再估计去气象化趋势

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-4b8931ad

## 复用场景
- E45
