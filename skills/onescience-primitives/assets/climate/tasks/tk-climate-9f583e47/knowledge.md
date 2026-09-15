# 骨架任务：生成逐时轮毂风场

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“生成逐时轮毂风场”，完成从近地面风、NWP、地形、轮毂高度到轮毂高度风速风向及误差范围的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{RUN_CONFIG}、{TARGET_HUB_HEIGHTS}、{OUTPUT_INTERVAL}执行生成逐时轮毂风场，将近地面风、NWP、地形、轮毂高度转换为轮毂高度风速风向及误差范围。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {RUN_CONFIG} | required=True | type=str | var_name=轮毂风预报配置 | hint=输入轮毂风预报配置。 | default=None
- {TARGET_HUB_HEIGHTS} | required=True | type=str | var_name=目标轮毂高度 | hint=输入目标轮毂高度。 | default=None
- {OUTPUT_INTERVAL} | required=True | type=str | var_name=输出间隔 | hint=输入结果输出间隔。 | default=None

## 产出
- 中间状态与运行日志
- 生成逐时轮毂风场结果
- 资源和退出状态记录

## 质量门禁 quality_gate
- 功率、负荷或辐照度输出满足物理边界
- 核心计算未读取任务截止时间之后的数据
- 目标区域和时段内结果完整且无重复或错位
- 输出目标是轮毂高度风速且不转换为风电功率
- 配置、随机种子、日志和中间状态能够追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-17b860f6

## 复用场景
- E26
