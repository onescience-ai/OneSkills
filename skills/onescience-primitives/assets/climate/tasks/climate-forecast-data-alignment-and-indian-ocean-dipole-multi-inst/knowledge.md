# 实例任务：起报资料时空对齐与样本构造 @ E78

- domain: climate
- 骨架: climate-forecast-data-alignment-and-sample-construction-task
- 场景: climate-indian-ocean-dipole-multi-season-index-forecast-scenario (E78)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- E78
- 关联论文: Multi-task machine learning improves multi-seasonal prediction of the Indian Ocean Dipole | doi:

## 本实例步骤描述
执行“起报资料时空对齐与样本构造”，统一印度洋—太平洋海温、热含量和风场的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 本实例执行 prompt
依据{SPATIOTEMPORAL_GRID}、{PREPROCESS_CONFIG}、{MISSING_VALUE_POLICY}完成起报资料时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 本实例输入槽
- {SPATIOTEMPORAL_GRID} | required=True | type=str | var_name=时空网格 | hint=输入时空网格规格。 | default=None
- {PREPROCESS_CONFIG} | required=True | type=str | var_name=预处理配置 | hint=输入预处理配置。 | default=None
- {MISSING_VALUE_POLICY} | required=True | type=str | var_name=缺测处理规则 | hint=输入缺测处理规则。 | default=None

## 本实例产出
- 对齐后的标准输入
- 掩膜与样本索引
- 预处理转换记录

## 本实例质量门禁
- 预处理后的时间轴、坐标、单位和形状可检查
- 每项插值、归一化、掩膜和缺测处理均有记录
- 不存在由验证资料或未来资料造成的信息泄漏
- 时次、变量、单位和坐标满足任务契约

## 可调资源（edge:resource，仅真实存在）
- models/matern-gaussian-process-regression
- models/spatial-and-temporal-deep-learning-models-for-fire-prediction

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
