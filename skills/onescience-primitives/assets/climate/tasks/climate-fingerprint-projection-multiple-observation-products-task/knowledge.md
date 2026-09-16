# 骨架任务：将指纹投影到多套观测产品

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“将指纹投影到多套观测产品”，完成从气候模式大集合日降水、观测日降水到人为指纹得分、空间贡献和检测时间序列的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{FINGERPRINT_CONFIG}、{RESAMPLING_COUNT}、{SIGNIFICANCE_LEVEL}执行将指纹投影到多套观测产品，将气候模式大集合日降水、观测日降水转换为人为指纹得分、空间贡献和检测时间序列。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {FINGERPRINT_CONFIG} | required=True | type=str | var_name=指纹投影配置 | hint=输入指纹投影配置。 | default=None
- {RESAMPLING_COUNT} | required=True | type=str | var_name=重采样次数 | hint=输入重采样次数。 | default=1000
- {SIGNIFICANCE_LEVEL} | required=True | type=str | var_name=显著性水平 | hint=输入显著性水平。 | default=0.05

## 产出
- 中间状态与运行日志
- 将指纹投影到多套观测产品结果
- 资源和退出状态记录

## 质量门禁 quality_gate
- 冻结训练得到的指纹后才投影到独立观测产品
- 核心计算未读取任务截止时间之后的数据
- 检测、关联和因果归因结论被明确区分
- 目标区域和时段内结果完整且无重复或错位
- 配置、随机种子、日志和中间状态能够追溯

## 可调资源（edge:resource，仅真实存在）
- datasets/smap-level-3-passive-soil-moisture-products
- models/1d-cnn-based-groundwater-level-prediction
- models/importance-sampling-strategy-for-extreme-events
- tools/multi-level-b-spline-analysis-mba

## 实例任务（本骨架在各场景的实例化）
- climate-fingerprint-projection-daily-precipitation-field-inst

## 复用场景
- E94
