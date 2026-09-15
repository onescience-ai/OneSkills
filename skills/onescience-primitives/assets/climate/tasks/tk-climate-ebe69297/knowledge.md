# 骨架任务：天气暴露和目标观测时空对齐与样本构造

- domain: climate
- 复用场景数: 4
- 实例任务数: 4

## 步骤描述（跨场景聚合去重）
- 执行“天气暴露和目标观测时空对齐与样本构造”，统一历史用水、天气、日历、人口与政策情景的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“天气暴露和目标观测时空对齐与样本构造”，统一多点田间试验、品种基因型、历史天气和生育期特征的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“天气暴露和目标观测时空对齐与样本构造”，统一截至签发日天气、土壤、种植管理和历史产量的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“天气暴露和目标观测时空对齐与样本构造”，统一气象历史与预报、病例序列、季节人口信息的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 执行 prompt（跨场景聚合去重）
- 依据{ALIGNMENT_CONFIG}、{CONFOUNDER_POLICY}、{SPLIT_PROTOCOL}完成天气暴露和目标观测时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。
- 依据{ALIGNMENT_CONFIG}、{TREND_FEATURE_POLICY}、{FORWARD_SPLIT_PROTOCOL}完成天气暴露和目标观测时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。
- 依据{PHENOLOGY_CONFIG}、{ENVIRONMENT_ALIGNMENT}、{SPLIT_PROTOCOL}完成天气暴露和目标观测时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 输入槽（var/hint/default）
- {PHENOLOGY_CONFIG} | required=True | type=str | var_name=生育期配置 | hint=输入作物生育期配置。 | default=None
- {ENVIRONMENT_ALIGNMENT} | required=True | type=str | var_name=环境对齐配置 | hint=输入基因环境对齐配置。 | default=None
- {SPLIT_PROTOCOL} | required=True | type=str | var_name=数据划分协议 | hint=输入时空划分协议。 | default=None
- {ALIGNMENT_CONFIG} | required=True | type=str | var_name=县域时空对齐 | hint=输入县域时空对齐配置。 | default=None
- {CONFOUNDER_POLICY} | required=False | type=str | var_name=混杂因素规则 | hint=输入混杂因素处理规则。 | default=None
- {TREND_FEATURE_POLICY} | required=True | type=str | var_name=产量趋势规则 | hint=输入产量趋势处理规则。 | default=None
- {FORWARD_SPLIT_PROTOCOL} | required=True | type=str | var_name=前推验证协议 | hint=输入按年份前推协议。 | default=None

## 产出
- 对齐后的标准输入
- 掩膜与样本索引
- 预处理转换记录

## 质量门禁 quality_gate
- 不存在由验证资料或未来资料造成的信息泄漏
- 每项插值、归一化、掩膜和缺测处理均有记录
- 训练验证划分阻断同一地点或事件的信息泄漏
- 预处理后的时间轴、坐标、单位和形状可检查

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-2f0651d6
- it-b055bd08
- it-e65fae7f
- it-ff55ac4d

## 复用场景
- E98
- E62
- E43
- E58
