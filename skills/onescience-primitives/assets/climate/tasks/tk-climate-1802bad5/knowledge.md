# 骨架任务：反演瞬时雨强并累积到目标时段

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“反演瞬时雨强并累积到目标时段”，完成从雷达多仰角反射率、雨量计观测、质量标识到当前雨强格点、站点降水与质量掩膜的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{RUN_CONFIG}、{OUTPUT_RESOLUTION}、{DECISION_THRESHOLD}执行反演瞬时雨强并累积到目标时段，将雷达多仰角反射率、雨量计观测、质量标识转换为当前雨强格点、站点降水与质量掩膜。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {OUTPUT_RESOLUTION} | required=True | type=str | var_name=输出分辨率 | hint=输入输出分辨率。 | default=None
- {DECISION_THRESHOLD} | required=False | type=str | var_name=诊断阈值 | hint=输入诊断判定阈值。 | default=None

## 产出
- 中间状态与运行日志
- 反演瞬时雨强并累积到目标时段结果
- 资源和退出状态记录

## 质量门禁 quality_gate
- 参考定义或标签未泄漏到待诊断样本
- 核心计算未读取任务截止时间之后的数据
- 目标区域和时段内结果完整且无重复或错位
- 配置、随机种子、日志和中间状态能够追溯
- 雷达垂直结构和雨量计校准对雨强结果可追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-4ac83a70

## 复用场景
- E34
