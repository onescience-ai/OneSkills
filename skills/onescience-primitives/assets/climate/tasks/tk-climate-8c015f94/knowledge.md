# 骨架任务：逐瓦片生成土地覆盖类别概率

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 按冻结配置执行“逐瓦片生成土地覆盖类别概率”，完成从多时相光学卫星影像、辅助地理信息和标签到10米土地覆盖类别概率图的核心计算并保存逐阶段日志。

## 执行 prompt（跨场景聚合去重）
- 依据{RUN_CONFIG}、{CLASS_LEGEND}、{MOSAIC_POLICY}执行逐瓦片生成土地覆盖类别概率，将多时相光学卫星影像、辅助地理信息和标签转换为10米土地覆盖类别概率图。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 输入槽（var/hint/default）
- {RUN_CONFIG} | required=True | type=str | var_name=制图运行配置 | hint=输入土地覆盖制图配置。 | default=None
- {CLASS_LEGEND} | required=True | type=str | var_name=多类标签体系 | hint=输入土地覆盖类别体系。 | default=None
- {MOSAIC_POLICY} | required=True | type=str | var_name=拼接处理规则 | hint=输入拼接处理规则。 | default=None

## 产出
- 中间状态与运行日志
- 资源和退出状态记录
- 逐瓦片生成土地覆盖类别概率结果

## 质量门禁 quality_gate
- 核心计算未读取任务截止时间之后的数据
- 瓦片拼接后保留多类概率和统一图例编码
- 目标区域和时段内结果完整且无重复或错位
- 输出坐标、分辨率、无效值和置信信息完整
- 配置、随机种子、日志和中间状态能够追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-3675ee17

## 复用场景
- E71
