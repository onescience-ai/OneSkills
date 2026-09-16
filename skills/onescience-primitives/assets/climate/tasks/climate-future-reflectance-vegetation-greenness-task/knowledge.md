# 骨架任务：生成未来多时次反射率与植被绿度

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“生成未来多时次反射率与植被绿度”，完成从历史多光谱影像、天气驱动和静态地形到未来反射率、NDVI或植被状态序列的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{RUN_CONFIG}、{OUTPUT_INTERVAL}、{CLOUD_GAP_POLICY}执行生成未来多时次反射率与植被绿度，将历史多光谱影像、天气驱动和静态地形转换为未来反射率、NDVI或植被状态序列。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {OUTPUT_INTERVAL} | required=True | type=str | var_name=输出间隔 | hint=输入结果输出间隔。 | default=None
- {CLOUD_GAP_POLICY} | required=True | type=str | var_name=云缺口处理规则 | hint=输入云缺口处理规则。 | default=None

## 产出
- 中间状态与运行日志
- 生成未来多时次反射率与植被绿度结果
- 资源和退出状态记录

## 质量门禁 quality_gate
- 核心计算未读取任务截止时间之后的数据
- 每个周尺度提前量均输出连续反射率与绿度场
- 滚动过程中未读取起报时间之后的观测或分析资料
- 目标区域和时段内结果完整且无重复或错位
- 配置、随机种子、日志和中间状态能够追溯

## 可调资源（edge:resource，仅真实存在）
- datasets/modis-myd13a3-ndvi-product
- models/ensemble-model-output-statistics-emos-post-processing

## 实例任务（本骨架在各场景的实例化）
- climate-future-reflectance-vegetation-satellite-weather-driven-inst

## 复用场景
- E39
