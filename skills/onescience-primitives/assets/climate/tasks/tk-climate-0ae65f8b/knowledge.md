# 骨架任务：回推历史NDVI并填补传感器断点

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“回推历史NDVI并填补传感器断点”，完成从重叠期AVHRR与MODIS NDVI、质量标志和时空特征到校准后的连续长期NDVI序列的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{RECONSTRUCTION_CONFIG}、{OUTPUT_RESOLUTION}、{UNCERTAINTY_CONFIG}执行回推历史NDVI并填补传感器断点，将重叠期AVHRR与MODIS NDVI、质量标志和时空特征转换为校准后的连续长期NDVI序列。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {RECONSTRUCTION_CONFIG} | required=True | type=str | var_name=重建配置 | hint=输入缺口重建配置。 | default=None
- {OUTPUT_RESOLUTION} | required=True | type=str | var_name=输出分辨率 | hint=输入输出分辨率。 | default=None
- {UNCERTAINTY_CONFIG} | required=False | type=str | var_name=不确定性配置 | hint=输入不确定性估计配置。 | default=None

## 产出
- 中间状态与运行日志
- 回推历史NDVI并填补传感器断点结果
- 资源和退出状态记录

## 质量门禁 quality_gate
- 核心计算未读取任务截止时间之后的数据
- 目标区域和时段内结果完整且无重复或错位
- 观测位置保持原值且缺口结果无拼接突变
- 配置、随机种子、日志和中间状态能够追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-550aaf01

## 复用场景
- E91
