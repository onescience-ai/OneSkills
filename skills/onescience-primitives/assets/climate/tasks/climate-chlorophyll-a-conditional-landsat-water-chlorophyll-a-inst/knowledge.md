# 实例任务：反演叶绿素a条件分布或点估计 @ E73

- domain: climate
- 骨架: climate-chlorophyll-a-conditional-distribution-point-retrieval-task
- 场景: climate-landsat-water-chlorophyll-a-probabilistic-retrieval-scenario (E73)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E73
- 关联论文: A Chlorophyll-a Algorithm for Landsat-8 Based on Mixture Density Networks | doi:

## 本实例步骤描述
按冻结配置执行“反演叶绿素a条件分布或点估计”，完成从Landsat水色波段、观测几何和水样叶绿素标签到叶绿素a浓度、分位数及质量掩膜的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{DECISION_THRESHOLD}、{UNCERTAINTY_CONFIG}执行反演叶绿素a条件分布或点估计，将Landsat水色波段、观测几何和水样叶绿素标签转换为叶绿素a浓度、分位数及质量掩膜。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {DECISION_THRESHOLD} | required=False | type=str | var_name=判定阈值 | hint=输入分类或检测阈值。 | default=None
- {UNCERTAINTY_CONFIG} | required=False | type=str | var_name=不确定性配置 | hint=输入不确定性估计配置。 | default=None

## 本实例产出
- 反演叶绿素a条件分布或点估计结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 输出坐标、分辨率、无效值和置信信息完整

## 可调资源（edge:resource，仅真实存在）
- datasets/gleam-v3-8a-global-land-evaporation-dataset
- tools/ecmwf-hres

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
