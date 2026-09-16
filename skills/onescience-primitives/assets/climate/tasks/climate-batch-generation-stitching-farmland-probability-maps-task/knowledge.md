# 骨架任务：批量生成并拼接农田概率图

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“批量生成并拼接农田概率图”，完成从多季节Landsat影像、植被指数和训练样本到30米农田范围图及区域面积的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{RUN_CONFIG}、{CROPLAND_THRESHOLD}、{AREA_STATISTICS_UNITS}执行批量生成并拼接农田概率图，将多季节Landsat影像、植被指数和训练样本转换为30米农田范围图及区域面积。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {RUN_CONFIG} | required=True | type=str | var_name=制图运行配置 | hint=输入农田制图配置。 | default=None
- {CROPLAND_THRESHOLD} | required=True | type=str | var_name=农田判定阈值 | hint=输入农田判定阈值。 | default=None
- {AREA_STATISTICS_UNITS} | required=True | type=str | var_name=面积统计单位 | hint=输入面积统计单位。 | default=None

## 产出
- 中间状态与运行日志
- 批量生成并拼接农田概率图结果
- 资源和退出状态记录

## 质量门禁 quality_gate
- 二分类概率、农田掩膜和面积统计同步生成
- 核心计算未读取任务截止时间之后的数据
- 目标区域和时段内结果完整且无重复或错位
- 输出坐标、分辨率、无效值和置信信息完整
- 配置、随机种子、日志和中间状态能够追溯

## 可调资源（edge:resource，仅真实存在）
- datasets/gleam-v3-8a-global-land-evaporation-dataset
- models/ensemble-model-output-statistics-emos-post-processing
- tools/ecmwf-hres

## 实例任务（本骨架在各场景的实例化）
- climate-batch-generation-stitching-30m-large-scale-farmland-inst

## 复用场景
- E56
