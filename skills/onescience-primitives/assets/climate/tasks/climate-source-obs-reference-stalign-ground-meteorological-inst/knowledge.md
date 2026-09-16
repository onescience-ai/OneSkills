# 实例任务：源观测和参考资料时空对齐与样本构造 @ E63

- domain: climate
- 骨架: climate-source-obs-reference-stalign-sample-task
- 场景: climate-ground-meteorological-driven-daily-total-solar-radiation-scenario (E63)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- E63
- 关联论文: Artificial neural network model with different backpropagation algorithms and meteorological data for solar radiation prediction | doi:; Solar Radiation Prediction Using Different Machine Learning Algorithms and Implications for Extreme Climate Events | doi:; Global solar radiation prediction using artificial neural network models for New Zealand | doi:

## 本实例步骤描述
执行“源观测和参考资料时空对齐与样本构造”，统一站点日温度、湿度、风速及可选时间特征的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 本实例执行 prompt
依据{ALIGNMENT_CONFIG}、{QUALITY_CONTROL}、{REFERENCE_DEFINITION}完成源观测和参考资料时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 本实例输入槽
- {ALIGNMENT_CONFIG} | required=True | type=str | var_name=时空对齐配置 | hint=输入时空对齐配置。 | default=None
- {QUALITY_CONTROL} | required=True | type=str | var_name=质量控制配置 | hint=输入质量控制配置。 | default=None
- {REFERENCE_DEFINITION} | required=False | type=str | var_name=参考定义 | hint=输入标签或参考定义。 | default=None

## 本实例产出
- 对齐后的标准输入
- 掩膜与样本索引
- 预处理转换记录

## 本实例质量门禁
- 预处理后的时间轴、坐标、单位和形状可检查
- 每项插值、归一化、掩膜和缺测处理均有记录
- 不存在由验证资料或未来资料造成的信息泄漏
- 同期资料在坐标、单位和质量标志上严格对齐

## 可调资源（edge:resource，仅真实存在）
- datasets/south-korea-air-quality-and-weather-monitoring-dataset

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
