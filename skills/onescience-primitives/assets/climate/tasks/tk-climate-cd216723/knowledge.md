# 骨架任务：输出像元或对象初生概率

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“输出像元或对象初生概率”，完成从多时次多光谱卫星云图、对流初生标签到初生概率格点、对流对象和时间标记的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{RUN_CONFIG}、{OUTPUT_RESOLUTION}、{DECISION_THRESHOLD}执行输出像元或对象初生概率，将多时次多光谱卫星云图、对流初生标签转换为初生概率格点、对流对象和时间标记。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {OUTPUT_RESOLUTION} | required=True | type=str | var_name=输出分辨率 | hint=输入输出分辨率。 | default=None
- {DECISION_THRESHOLD} | required=False | type=str | var_name=诊断阈值 | hint=输入诊断判定阈值。 | default=None

## 产出
- 中间状态与运行日志
- 资源和退出状态记录
- 输出像元或对象初生概率结果

## 质量门禁 quality_gate
- 参考定义或标签未泄漏到待诊断样本
- 核心计算未读取任务截止时间之后的数据
- 目标区域和时段内结果完整且无重复或错位
- 配置、随机种子、日志和中间状态能够追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-a96841c6

## 复用场景
- E80
