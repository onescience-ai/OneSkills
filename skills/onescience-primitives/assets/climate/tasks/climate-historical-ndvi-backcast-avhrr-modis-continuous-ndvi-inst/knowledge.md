# 实例任务：回推历史NDVI并填补传感器断点 @ E91

- domain: climate
- 骨架: climate-historical-ndvi-backcast-sensor-gap-filling-task
- 场景: climate-avhrr-modis-continuous-ndvi-historical-fusion-reconstruction-scenario (E91)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E91
- 关联论文: Neural networks as a tool for constructing continuous NDVI time series from AVHRR and MODIS | doi:

## 本实例步骤描述
按冻结配置执行“回推历史NDVI并填补传感器断点”，完成从重叠期AVHRR与MODIS NDVI、质量标志和时空特征到校准后的连续长期NDVI序列的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RECONSTRUCTION_CONFIG}、{OUTPUT_RESOLUTION}、{UNCERTAINTY_CONFIG}执行回推历史NDVI并填补传感器断点，将重叠期AVHRR与MODIS NDVI、质量标志和时空特征转换为校准后的连续长期NDVI序列。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RECONSTRUCTION_CONFIG} | required=True | type=str | var_name=重建配置 | hint=输入缺口重建配置。 | default=None
- {OUTPUT_RESOLUTION} | required=True | type=str | var_name=输出分辨率 | hint=输入输出分辨率。 | default=None
- {UNCERTAINTY_CONFIG} | required=False | type=str | var_name=不确定性配置 | hint=输入不确定性估计配置。 | default=None

## 本实例产出
- 回推历史NDVI并填补传感器断点结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 观测位置保持原值且缺口结果无拼接突变

## 可调资源（edge:resource，仅真实存在）
- datasets/gtws-mlrec-machine-learning-based-global-terrestrial-water-storage-anomaly-reconstruction-dataset-and-workflow
- datasets/modis-myd13a3-ndvi-product
- models/ensemble-model-output-statistics-emos-post-processing
- models/swe-reconstruction-using-energy-balance-model

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
