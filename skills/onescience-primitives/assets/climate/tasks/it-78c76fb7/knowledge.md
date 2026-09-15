# 实例任务：构造生育期特征并生成县域产量分布 @ E58

- domain: climate
- 骨架: tk-climate-ed63ab71
- 场景: sc-66c922e3 (E58)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E58
- 关联论文: Forecasting Corn Yield With Machine Learning Ensembles | doi:; Maize yield forecasting by linear regression and artificial neural networks in Jilin, China | doi:

## 本实例步骤描述
按冻结配置执行“构造生育期特征并生成县域产量分布”，完成从截至签发日天气、土壤、种植管理和历史产量到县域玉米单产及不确定性的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{FORECAST_CONFIG}、{FUTURE_WEATHER_POLICY}、{UNCERTAINTY_CONFIG}执行构造生育期特征并生成县域产量分布，将截至签发日天气、土壤、种植管理和历史产量转换为县域玉米单产及不确定性。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {FORECAST_CONFIG} | required=True | type=str | var_name=产量预测配置 | hint=输入产量预测配置。 | default=None
- {FUTURE_WEATHER_POLICY} | required=True | type=str | var_name=未来天气规则 | hint=输入未来天气使用规则。 | default=None
- {UNCERTAINTY_CONFIG} | required=True | type=str | var_name=不确定性配置 | hint=输入不确定性估计配置。 | default=None

## 本实例产出
- 构造生育期特征并生成县域产量分布结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 预测关系与因果归因声明严格区分
- 核心运行必须生成县域产量点估计和不确定性分布

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
