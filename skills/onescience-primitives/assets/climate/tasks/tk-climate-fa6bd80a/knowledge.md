# 骨架任务：生成逐日蒸散发预报

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“生成逐日蒸散发预报”，完成从温度湿度风速辐射观测与预报到未来7天参考蒸散发序列的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{RUN_CONFIG}、{FORECAST_DAYS}、{OUTPUT_INTERVAL}执行生成逐日蒸散发预报，将温度湿度风速辐射观测与预报转换为未来7天参考蒸散发序列。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {RUN_CONFIG} | required=True | type=str | var_name=蒸散发预报配置 | hint=输入蒸散发预报配置。 | default=None
- {FORECAST_DAYS} | required=True | type=str | var_name=预报天数 | hint=输入预报天数。 | default=7
- {OUTPUT_INTERVAL} | required=True | type=str | var_name=输出间隔 | hint=输入逐日输出间隔。 | default=1天

## 产出
- 中间状态与运行日志
- 生成逐日蒸散发预报结果
- 资源和退出状态记录

## 质量门禁 quality_gate
- 完整生成未来七个逐日参考蒸散发值
- 核心计算未读取任务截止时间之后的数据
- 水量、状态范围和洪峰时序不存在非物理异常
- 目标区域和时段内结果完整且无重复或错位
- 配置、随机种子、日志和中间状态能够追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-55c16904

## 复用场景
- E66
