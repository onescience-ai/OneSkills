# 骨架任务：生成未来情景高分辨率场

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“生成未来情景高分辨率场”，完成从CMIP6粗网格场、区域观测或再分析、地形、排放情景到区域高分辨率温度降水投影的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{RUN_CONFIG}、{ENSEMBLE_SIZE}、{OUTPUT_INTERVAL}执行生成未来情景高分辨率场，将CMIP6粗网格场、区域观测或再分析、地形、排放情景转换为区域高分辨率温度降水投影。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {ENSEMBLE_SIZE} | required=True | type=str | var_name=生成成员数 | hint=输入生成成员数量。 | default=1
- {OUTPUT_INTERVAL} | required=True | type=str | var_name=输出间隔 | hint=输入结果输出间隔。 | default=None

## 产出
- 中间状态与运行日志
- 生成未来情景高分辨率场结果
- 资源和退出状态记录

## 质量门禁 quality_gate
- 核心计算未读取任务截止时间之后的数据
- 目标区域和时段内结果完整且无重复或错位
- 输出均值、极端尾部和空间频谱均可检查
- 配置、随机种子、日志和中间状态能够追溯

## 可调资源（edge:resource，仅真实存在）
- datasets/ERA5

## 实例任务（本骨架在各场景的实例化）
- it-9d296797

## 复用场景
- E38
