# 实例任务：预报实况样本时空对齐与样本构造 @ E24

- domain: climate
- 骨架: tk-climate-7d33370a
- 场景: sc-fe3c0d54 (E24)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- E24
- 关联论文: Improving Model Chain Approaches for Probabilistic Solar Energy Forecasting through Post-processing and Machine Learning | doi:; Post-processing numerical weather prediction ensembles for probabilistic solar irradiance forecasting | doi:; Comparison of statistical post-processing methods for probabilistic NWP forecasts of solar radiation | doi:; Machine-learning-based probabilistic forecasting of solar irradiance in Chile | doi:

## 本实例步骤描述
执行“预报实况样本时空对齐与样本构造”，统一集合NWP辐射、历史观测与误差的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 本实例执行 prompt
依据{MATCHING_CONFIG}、{SPLIT_PROTOCOL}、{MISSING_VALUE_POLICY}完成预报实况样本时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 本实例输入槽
- {MATCHING_CONFIG} | required=True | type=str | var_name=预报实况配对 | hint=输入预报实况配对规则。 | default=None
- {SPLIT_PROTOCOL} | required=True | type=str | var_name=数据划分协议 | hint=输入时间划分协议。 | default=None
- {MISSING_VALUE_POLICY} | required=True | type=str | var_name=缺测处理规则 | hint=输入缺测处理规则。 | default=None

## 本实例产出
- 对齐后的标准输入
- 掩膜与样本索引
- 预处理转换记录

## 本实例质量门禁
- 预处理后的时间轴、坐标、单位和形状可检查
- 每项插值、归一化、掩膜和缺测处理均有记录
- 不存在由验证资料或未来资料造成的信息泄漏
- 校准、验证和测试时段互斥且无未来信息泄漏

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
