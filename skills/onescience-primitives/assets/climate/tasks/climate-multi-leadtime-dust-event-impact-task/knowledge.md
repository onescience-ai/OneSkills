# 骨架任务：生成多时效沙尘发生、强度和影响区

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“生成多时效沙尘发生、强度和影响区”，完成从气象预报、气溶胶观测、地表与沙尘历史到沙尘概率、浓度等级和影响区的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{RUN_CONFIG}、{LEAD_TIMES}、{WARNING_THRESHOLDS}执行生成多时效沙尘发生、强度和影响区，将气象预报、气溶胶观测、地表与沙尘历史转换为沙尘概率、浓度等级和影响区。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {RUN_CONFIG} | required=True | type=str | var_name=沙尘预警配置 | hint=输入沙尘预警配置。 | default=None
- {LEAD_TIMES} | required=True | type=str | var_name=目标提前期 | hint=输入目标提前期清单。 | default=None
- {WARNING_THRESHOLDS} | required=True | type=str | var_name=沙尘预警阈值 | hint=输入沙尘预警阈值。 | default=None

## 产出
- 中间状态与运行日志
- 生成多时效沙尘发生、强度和影响区结果
- 资源和退出状态记录

## 质量门禁 quality_gate
- 核心计算未读取任务截止时间之后的数据
- 每个提前期均输出沙尘发生、强度和影响区域
- 目标区域和时段内结果完整且无重复或错位
- 配置、随机种子、日志和中间状态能够追溯
- 预警阈值在独立验证集上冻结后评估

## 可调资源（edge:resource，仅真实存在）
- models/dynamic-pre-training-for-time-series-dynpt
- tools/ecmwf-hres

## 实例任务（本骨架在各场景的实例化）
- climate-multi-leadtime-dust-event-multi-source-observation-inst

## 复用场景
- E92
