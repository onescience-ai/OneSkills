# 实例任务：逐像元生成NH3总柱浓度 @ E79

- domain: climate
- 骨架: tk-climate-349b036b
- 场景: sc-51f44d8d (E79)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E79
- 关联论文: Version 2 of the IASI NH 3 neural network retrieval algorithm- near-real-time and reanalysed datasets | doi:

## 本实例步骤描述
按冻结配置执行“逐像元生成NH3总柱浓度”，完成从IASI红外光谱、热力廓线和观测几何到NH3总柱浓度、误差及质量标志的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{DECISION_THRESHOLD}、{UNCERTAINTY_CONFIG}执行逐像元生成NH3总柱浓度，将IASI红外光谱、热力廓线和观测几何转换为NH3总柱浓度、误差及质量标志。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {DECISION_THRESHOLD} | required=False | type=str | var_name=判定阈值 | hint=输入分类或检测阈值。 | default=None
- {UNCERTAINTY_CONFIG} | required=False | type=str | var_name=不确定性配置 | hint=输入不确定性估计配置。 | default=None

## 本实例产出
- 逐像元生成NH3总柱浓度结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 输出坐标、分辨率、无效值和置信信息完整

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
