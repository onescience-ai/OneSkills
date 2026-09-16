# 实例任务：观测强迫样本时空对齐与样本构造 @ E45

- domain: climate
- 骨架: climate-observation-forced-sample-alignment-and-sampling-task
- 场景: climate-ozone-and-particulate-matter-historical-series-meteorological-scenario (E45)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- E45
- 关联论文: A machine learning approach to quantify meteorological drivers of ozone pollution in China from 2015 to 2019 | doi:; Assessing the impact of clean air action on air quality trends in Beijing using a machine learning technique | doi:; Meteorology-driven variability of air pollution (PM1) revealed with explainable machine learning | doi:

## 本实例步骤描述
执行“观测强迫样本时空对齐与样本构造”，统一历史污染观测、同期气象和时间特征的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 本实例执行 prompt
依据{ALIGNMENT_CONFIG}、{SPLIT_PROTOCOL}、{CONFOUNDER_POLICY}完成观测强迫样本时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 本实例输入槽
- {ALIGNMENT_CONFIG} | required=True | type=str | var_name=时空对齐配置 | hint=输入时空对齐配置。 | default=None
- {SPLIT_PROTOCOL} | required=True | type=str | var_name=数据划分协议 | hint=输入独立划分协议。 | default=None
- {CONFOUNDER_POLICY} | required=False | type=str | var_name=混杂因素规则 | hint=输入混杂因素处理规则。 | default=None

## 本实例产出
- 对齐后的标准输入
- 掩膜与样本索引
- 预处理转换记录

## 本实例质量门禁
- 预处理后的时间轴、坐标、单位和形状可检查
- 每项插值、归一化、掩膜和缺测处理均有记录
- 不存在由验证资料或未来资料造成的信息泄漏
- 训练、检测和显著性评估样本相互独立

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
