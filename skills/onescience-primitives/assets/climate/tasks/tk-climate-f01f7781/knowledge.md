# 骨架任务：天气能源运行资料时空对齐与样本构造

- domain: climate
- 复用场景数: 4
- 实例任务数: 4

## 步骤描述（跨场景聚合去重）
- 执行“天气能源运行资料时空对齐与样本构造”，统一历史负荷、天气预报、日历与用户层级的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“天气能源运行资料时空对齐与样本构造”，统一多站历史功率、天气预报、电站容量属性的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“天气能源运行资料时空对齐与样本构造”，统一天空图像、卫星云图、历史辐照度的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“天气能源运行资料时空对齐与样本构造”，统一近地面风、NWP、地形、轮毂高度的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 执行 prompt（跨场景聚合去重）
- 依据{ALIGNMENT_CONFIG}、{CAPACITY_POLICY}、{MISSING_VALUE_POLICY}完成天气能源运行资料时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。
- 依据{ALIGNMENT_CONFIG}、{HIERARCHY_CONFIG}、{MISSING_VALUE_POLICY}完成天气能源运行资料时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。
- 依据{IMAGE_CALIBRATION_CONFIG}、{TIME_ALIGNMENT_CONFIG}、{CLEAR_SKY_CONFIG}完成天气能源运行资料时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。
- 依据{TERRAIN_ALIGNMENT_CONFIG}、{VERTICAL_MAPPING_CONFIG}、{MISSING_VALUE_POLICY}完成天气能源运行资料时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 输入槽（var/hint/default）
- {TERRAIN_ALIGNMENT_CONFIG} | required=True | type=str | var_name=地形对齐配置 | hint=输入地形对齐配置。 | default=None
- {VERTICAL_MAPPING_CONFIG} | required=True | type=str | var_name=垂向映射配置 | hint=输入轮毂高度映射配置。 | default=None
- {MISSING_VALUE_POLICY} | required=True | type=str | var_name=缺测处理规则 | hint=输入缺测处理规则。 | default=None
- {ALIGNMENT_CONFIG} | required=True | type=str | var_name=天气负荷对齐 | hint=输入天气负荷对齐配置。 | default=None
- {CAPACITY_POLICY} | required=True | type=str | var_name=容量归一规则 | hint=输入容量归一规则。 | default=None
- {HIERARCHY_CONFIG} | required=True | type=str | var_name=层级汇总配置 | hint=输入层级汇总配置。 | default=None
- {IMAGE_CALIBRATION_CONFIG} | required=True | type=str | var_name=影像定标配置 | hint=输入影像定标配置。 | default=None
- {TIME_ALIGNMENT_CONFIG} | required=True | type=str | var_name=时间对齐配置 | hint=输入图像辐照度对齐配置。 | default=None
- {CLEAR_SKY_CONFIG} | required=True | type=str | var_name=晴空基准配置 | hint=输入晴空基准配置。 | default=None

## 产出
- 对齐后的标准输入
- 掩膜与样本索引
- 预处理转换记录

## 质量门禁 quality_gate
- 不存在由验证资料或未来资料造成的信息泄漏
- 容量、时区、采样间隔和缺测规则一致
- 每项插值、归一化、掩膜和缺测处理均有记录
- 预处理后的时间轴、坐标、单位和形状可检查

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-4727eee9
- it-54e679a4
- it-5c3b5949
- it-dbe4ae7b

## 复用场景
- E26
- E25
- E20
- E23
