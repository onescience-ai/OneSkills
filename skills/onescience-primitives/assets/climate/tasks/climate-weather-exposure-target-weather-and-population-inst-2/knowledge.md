# 实例任务：天气暴露和目标观测时空对齐与样本构造 @ E62

- domain: climate
- 骨架: climate-weather-exposure-target-observation-space-time-alignment-task
- 场景: climate-weather-and-population-change-driven-urban-monthly-daily-water-scenario (E62)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- E62
- 关联论文: Short-Term Urban Water Demand Prediction Considering Weather Factors | doi:; A Method for Predicting Long-Term Municipal Water Demands Under Climate Change | doi:; Urban Water Demand Prediction for a City That Suffers from Climate Change and Population Growth- Gauteng Province Case Study | doi:

## 本实例步骤描述
执行“天气暴露和目标观测时空对齐与样本构造”，统一历史用水、天气、日历、人口与政策情景的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 本实例执行 prompt
依据{ALIGNMENT_CONFIG}、{CONFOUNDER_POLICY}、{SPLIT_PROTOCOL}完成天气暴露和目标观测时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 本实例输入槽
- {ALIGNMENT_CONFIG} | required=True | type=str | var_name=时空对齐配置 | hint=输入时空对齐配置。 | default=None
- {CONFOUNDER_POLICY} | required=False | type=str | var_name=混杂因素规则 | hint=输入混杂因素处理规则。 | default=None
- {SPLIT_PROTOCOL} | required=True | type=str | var_name=数据划分协议 | hint=输入时空划分协议。 | default=None

## 本实例产出
- 对齐后的标准输入
- 掩膜与样本索引
- 预处理转换记录

## 本实例质量门禁
- 预处理后的时间轴、坐标、单位和形状可检查
- 每项插值、归一化、掩膜和缺测处理均有记录
- 不存在由验证资料或未来资料造成的信息泄漏
- 训练验证划分阻断同一地点或事件的信息泄漏

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
