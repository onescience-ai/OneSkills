# 实例任务：分阶段估计物候日期和不确定性 @ E67

- domain: climate
- 骨架: tk-climate-0e905287
- 场景: sc-b5341da3 (E67)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E67
- 关联论文: Machine learning modeling of plant phenology based on coupling satellite and gridded meteorological dataset | doi:; Deep Learning in Plant Phenological Research- A Systematic Literature Review | doi:

## 本实例步骤描述
按冻结配置执行“分阶段估计物候日期和不确定性”，完成从植被指数、气象累计量、雪盖、地形和物候观测到各物候阶段年积日及置信区间的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{DECISION_THRESHOLD}、{UNCERTAINTY_CONFIG}执行分阶段估计物候日期和不确定性，将植被指数、气象累计量、雪盖、地形和物候观测转换为各物候阶段年积日及置信区间。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {DECISION_THRESHOLD} | required=False | type=str | var_name=判定阈值 | hint=输入分类或检测阈值。 | default=None
- {UNCERTAINTY_CONFIG} | required=False | type=str | var_name=不确定性配置 | hint=输入不确定性估计配置。 | default=None

## 本实例产出
- 分阶段估计物候日期和不确定性结果
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
