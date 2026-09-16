# 骨架任务：起报资料时空对齐与样本构造

- domain: climate
- 复用场景数: 12
- 实例任务数: 12

## 步骤描述（跨场景聚合去重）
- 执行“起报资料时空对齐与样本构造”，统一全球分析场、随机扰动配置、目标时效的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“起报资料时空对齐与样本构造”，统一全球大气初态、云微物理状态、目标时效的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“起报资料时空对齐与样本构造”，统一全球大气初态、海陆边界状态、目标周的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“起报资料时空对齐与样本构造”，统一印度洋—太平洋海温、热含量和风场的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“起报资料时空对齐与样本构造”，统一历史区域风场、环境气象场、强风事件标签的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“起报资料时空对齐与样本构造”，统一历史多光谱影像、天气驱动和静态地形的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“起报资料时空对齐与样本构造”，统一多个季节起报初态、边界状态、气候基准的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“起报资料时空对齐与样本构造”，统一多站历史温湿风、站点位置与时间特征的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“起报资料时空对齐与样本构造”，统一气旋历史位置、强度元数据、风暴中心环境场的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“起报资料时空对齐与样本构造”，统一气旋强度历史、海温、环境大气场的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“起报资料时空对齐与样本构造”，统一热带风场、温度和对流异常历史的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“起报资料时空对齐与样本构造”，统一过去海温与海洋—大气状态序列的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 执行 prompt（跨场景聚合去重）
- 依据{CALENDAR_AND_GRID}、{CLIMATOLOGY_PERIOD}、{HINDCAST_PROTOCOL}完成起报资料时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。
- 依据{SPATIOTEMPORAL_GRID}、{PREPROCESS_CONFIG}、{MISSING_VALUE_POLICY}完成起报资料时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 输入槽（var/hint/default）
- {SPATIOTEMPORAL_GRID} | required=True | type=str | var_name=时空网格 | hint=输入时空网格规格。 | default=None
- {PREPROCESS_CONFIG} | required=True | type=str | var_name=预处理配置 | hint=输入预处理配置。 | default=None
- {MISSING_VALUE_POLICY} | required=True | type=str | var_name=缺测处理规则 | hint=输入缺测处理规则。 | default=None
- {CALENDAR_AND_GRID} | required=True | type=str | var_name=日历与网格 | hint=输入日历和网格规格。 | default=None
- {CLIMATOLOGY_PERIOD} | required=True | type=str | var_name=气候态基准期 | hint=输入气候态基准时段。 | default=None
- {HINDCAST_PROTOCOL} | required=True | type=str | var_name=回报划分协议 | hint=输入按年份回报协议。 | default=None

## 产出
- 对齐后的标准输入
- 掩膜与样本索引
- 预处理转换记录

## 质量门禁 quality_gate
- 不存在由验证资料或未来资料造成的信息泄漏
- 时次、变量、单位和坐标满足任务契约
- 每项插值、归一化、掩膜和缺测处理均有记录
- 预处理后的时间轴、坐标、单位和形状可检查

## 可调资源（edge:resource，仅真实存在）
- datasets/CMEMS
- models/matern-gaussian-process-regression
- models/spatial-and-temporal-deep-learning-models-for-fire-prediction

## 实例任务（本骨架在各场景的实例化）
- climate-forecast-data-alignment-and-enso-index-6-24-month-inst
- climate-forecast-data-alignment-and-global-1-15-day-ensemble-inst
- climate-forecast-data-alignment-and-global-1-6-month-seasonal-inst
- climate-forecast-data-alignment-and-global-10-42-day-subseasonal-inst
- climate-forecast-data-alignment-and-global-aviation-hazardous-inst
- climate-forecast-data-alignment-and-identified-tropical-cyclone-inst
- climate-forecast-data-alignment-and-identified-tropical-cyclone-inst-2
- climate-forecast-data-alignment-and-indian-ocean-dipole-multi-inst
- climate-forecast-data-alignment-and-mjo-intraseasonal-oscillatio-inst
- climate-forecast-data-alignment-and-multi-station-temp-humidity-inst
- climate-forecast-data-alignment-and-regional-short-to-medium-inst
- climate-forecast-data-alignment-and-satellite-weather-driven-inst

## 复用场景
- E9
- E19
- E7
- E3
- E47
- E88
- E95
- E39
- E78
- E41
- E50
- E30
