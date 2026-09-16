# 骨架任务：临近观测时空对齐与样本构造

- domain: climate
- 复用场景数: 6
- 实例任务数: 6

## 步骤描述（跨场景聚合去重）
- 执行“临近观测时空对齐与样本构造”，统一机场温湿风、能见度历史、NWP或CAMS预报的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“临近观测时空对齐与样本构造”，统一近期地面气象观测、站点位置、历史雷电标签的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“临近观测时空对齐与样本构造”，统一近期雷达卫星序列、站点观测、区域分析场的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“临近观测时空对齐与样本构造”，统一雷达体扫、闪电历史、对流环境场的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“临近观测时空对齐与样本构造”，统一雷达反射率序列、地面阵风记录、可选环境场的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“临近观测时空对齐与样本构造”，统一雷达回波序列、可选环境场、冰雹标签的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 执行 prompt（跨场景聚合去重）
- 依据{FRAME_INTERVAL}、{TARGET_GRID}、{QUALITY_CONTROL}、{MISSING_VALUE_POLICY}完成临近观测时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 输入槽（var/hint/default）
- {FRAME_INTERVAL} | required=True | type=str | var_name=观测帧间隔 | hint=输入观测帧间隔。 | default=None
- {TARGET_GRID} | required=True | type=str | var_name=目标网格 | hint=输入目标网格规格。 | default=None
- {QUALITY_CONTROL} | required=True | type=str | var_name=质量控制配置 | hint=输入质量控制配置。 | default=None
- {MISSING_VALUE_POLICY} | required=True | type=str | var_name=缺帧处理规则 | hint=输入缺帧处理规则。 | default=None

## 产出
- 对齐后的标准输入
- 掩膜与样本索引
- 预处理转换记录

## 质量门禁 quality_gate
- 不存在由验证资料或未来资料造成的信息泄漏
- 每项插值、归一化、掩膜和缺测处理均有记录
- 缺帧、异常回波和多源延迟已显式记录
- 预处理后的时间轴、坐标、单位和形状可检查

## 可调资源（edge:resource，仅真实存在）
- datasets/south-korea-air-quality-and-weather-monitoring-dataset

## 实例任务（本骨架在各场景的实例化）
- climate-near-observation-space-time-airport-fog-low-visibility-inst
- climate-near-observation-space-time-ground-meteorological-inst
- climate-near-observation-space-time-multi-source-observation-inst
- climate-near-observation-space-time-radar-and-environmental-inst
- climate-near-observation-space-time-weather-radar-convective-inst
- climate-near-observation-space-time-weather-radar-hail-probabili-inst

## 复用场景
- E52
- E8
- E83
- E85
- E33
- E72
