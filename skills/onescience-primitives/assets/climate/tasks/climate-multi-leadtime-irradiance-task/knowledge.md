# 骨架任务：生成多时效辐照度

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“生成多时效辐照度”，完成从天空图像、卫星云图、历史辐照度到多时效辐照度场或站点序列的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{RUN_CONFIG}、{LEAD_TIMES}、{OUTPUT_INTERVAL}执行生成多时效辐照度，将天空图像、卫星云图、历史辐照度转换为多时效辐照度场或站点序列。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {RUN_CONFIG} | required=True | type=str | var_name=辐照度预报配置 | hint=输入辐照度预报配置。 | default=None
- {LEAD_TIMES} | required=True | type=str | var_name=目标提前期 | hint=输入目标提前期清单。 | default=None
- {OUTPUT_INTERVAL} | required=True | type=str | var_name=输出间隔 | hint=输入结果输出间隔。 | default=None

## 产出
- 中间状态与运行日志
- 生成多时效辐照度结果
- 资源和退出状态记录

## 质量门禁 quality_gate
- 功率、负荷或辐照度输出满足物理边界
- 核心计算未读取任务截止时间之后的数据
- 每个分钟至小时提前期均生成辐照度而非光伏功率
- 目标区域和时段内结果完整且无重复或错位
- 配置、随机种子、日志和中间状态能够追溯

## 可调资源（edge:resource，仅真实存在）
- models/dynamic-pre-training-for-time-series-dynpt
- models/ensemble-model-output-statistics-emos-post-processing

## 实例任务（本骨架在各场景的实例化）
- climate-multi-leadtime-irradiance-sky-camera-satellite-solar-inst

## 复用场景
- E23
