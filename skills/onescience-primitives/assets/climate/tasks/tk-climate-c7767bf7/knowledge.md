# 骨架任务：滚动生成多周病例预测

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“滚动生成多周病例预测”，完成从气象历史与预报、病例序列、季节人口信息到周病例数、风险等级与概率的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{RUN_CONFIG}、{SCENARIO_CONDITIONS}、{UNCERTAINTY_CONFIG}执行滚动生成多周病例预测，将气象历史与预报、病例序列、季节人口信息转换为周病例数、风险等级与概率。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {SCENARIO_CONDITIONS} | required=False | type=str | var_name=情景条件 | hint=输入目标情景条件。 | default=None
- {UNCERTAINTY_CONFIG} | required=False | type=str | var_name=不确定性配置 | hint=输入不确定性估计配置。 | default=None

## 产出
- 中间状态与运行日志
- 滚动生成多周病例预测结果
- 资源和退出状态记录

## 质量门禁 quality_gate
- 核心计算未读取任务截止时间之后的数据
- 目标区域和时段内结果完整且无重复或错位
- 配置、随机种子、日志和中间状态能够追溯
- 预测关系与因果归因声明严格区分

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-3298a208

## 复用场景
- E43
