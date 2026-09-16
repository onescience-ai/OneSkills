# 实例任务：生成未来情景高分辨率场 @ E38

- domain: climate
- 骨架: climate-future-scenario-highres-field-task
- 场景: climate-cmip6-temperature-precipitation-regional-climate-downscaling-scenario (E38)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E38
- 关联论文: High-resolution downscaling of CMIP6 Earth system and global climate models using deep learning for Iberia | doi:; Projecting and Downscaling Future Temperature and Precipitation Based on CMIP6 Models Using Machine Learning in Hatay Province, Türkiye | doi:; On the suitability of deep convolutional neural networks for continental-wide downscaling of climate change projections | doi:

## 本实例步骤描述
按冻结配置执行“生成未来情景高分辨率场”，完成从CMIP6粗网格场、区域观测或再分析、地形、排放情景到区域高分辨率温度降水投影的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{ENSEMBLE_SIZE}、{OUTPUT_INTERVAL}执行生成未来情景高分辨率场，将CMIP6粗网格场、区域观测或再分析、地形、排放情景转换为区域高分辨率温度降水投影。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {ENSEMBLE_SIZE} | required=True | type=str | var_name=生成成员数 | hint=输入生成成员数量。 | default=1
- {OUTPUT_INTERVAL} | required=True | type=str | var_name=输出间隔 | hint=输入结果输出间隔。 | default=None

## 本实例产出
- 生成未来情景高分辨率场结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 输出均值、极端尾部和空间频谱均可检查

## 可调资源（edge:resource，仅真实存在）
- datasets/cesm2-large-ensemble
- datasets/ERA5
- datasets/large-ensemble-testbed
- models/crpsexp-loss-function-for-ensemble-forecasting
- models/ensemble-empirical-mode-decomposition-eemd
- models/ensemble-model-output-statistics-emos-post-processing

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
