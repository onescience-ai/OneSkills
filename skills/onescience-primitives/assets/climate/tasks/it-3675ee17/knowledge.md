# 实例任务：逐瓦片生成土地覆盖类别概率 @ E71

- domain: climate
- 骨架: tk-climate-8c015f94
- 场景: sc-99f6f860 (E71)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E71
- 关联论文: Dynamic World, Near real-time global 10 m land use land cover mapping | doi:

## 本实例步骤描述
按冻结配置执行“逐瓦片生成土地覆盖类别概率”，完成从多时相光学卫星影像、辅助地理信息和标签到10米土地覆盖类别概率图的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{CLASS_LEGEND}、{MOSAIC_POLICY}执行逐瓦片生成土地覆盖类别概率，将多时相光学卫星影像、辅助地理信息和标签转换为10米土地覆盖类别概率图。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=制图运行配置 | hint=输入土地覆盖制图配置。 | default=None
- {CLASS_LEGEND} | required=True | type=str | var_name=多类标签体系 | hint=输入土地覆盖类别体系。 | default=None
- {MOSAIC_POLICY} | required=True | type=str | var_name=拼接处理规则 | hint=输入拼接处理规则。 | default=None

## 本实例产出
- 逐瓦片生成土地覆盖类别概率结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 输出坐标、分辨率、无效值和置信信息完整
- 瓦片拼接后保留多类概率和统一图例编码

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
