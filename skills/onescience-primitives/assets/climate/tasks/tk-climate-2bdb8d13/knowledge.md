# 骨架任务：粗细分辨率资料时空对齐与样本构造

- domain: climate
- 复用场景数: 7
- 实例任务数: 7

## 步骤描述（跨场景聚合去重）
- 执行“粗细分辨率资料时空对齐与样本构造”，统一CMIP6粗网格场、区域观测或再分析、地形、排放情景的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“粗细分辨率资料时空对齐与样本构造”，统一原始NWP预报、起报分析、历史验证资料的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“粗细分辨率资料时空对齐与样本构造”，统一当日雪盖、微波亮温、地形和背景SWE的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“粗细分辨率资料时空对齐与样本构造”，统一粗分辨率LAI、气候情景、土地覆盖和高分辨率参考的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“粗细分辨率资料时空对齐与样本构造”，统一粗网格大气状态、地形与静态地理量的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“粗细分辨率资料时空对齐与样本构造”，统一粗网格小时降水、地形及可选环境场的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“粗细分辨率资料时空对齐与样本构造”，统一粗网格风场、地形、陆海掩膜和辅助大气量的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 执行 prompt（跨场景聚合去重）
- 依据{PAIRING_CONFIG}、{ACCUMULATION_POLICY}、{SPLIT_PROTOCOL}完成粗细分辨率资料时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。
- 依据{PAIRING_CONFIG}、{SPLIT_PROTOCOL}、{PREPROCESS_CONFIG}完成粗细分辨率资料时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。
- 依据{PAIRING_CONFIG}、{VARIABLE_LEVEL_MAPPING}、{SPLIT_PROTOCOL}完成粗细分辨率资料时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 输入槽（var/hint/default）
- {PAIRING_CONFIG} | required=True | type=str | var_name=粗细样本配对 | hint=输入粗细样本配对配置。 | default=None
- {SPLIT_PROTOCOL} | required=True | type=str | var_name=数据划分协议 | hint=输入时空划分协议。 | default=None
- {PREPROCESS_CONFIG} | required=True | type=str | var_name=预处理配置 | hint=输入预处理配置。 | default=None
- {ACCUMULATION_POLICY} | required=True | type=str | var_name=累计量转换规则 | hint=输入累计量转换规则。 | default=None
- {VARIABLE_LEVEL_MAPPING} | required=True | type=str | var_name=变量层次映射 | hint=输入变量层次映射。 | default=None

## 产出
- 对齐后的标准输入
- 掩膜与样本索引
- 预处理转换记录

## 质量门禁 quality_gate
- 不存在由验证资料或未来资料造成的信息泄漏
- 每项插值、归一化、掩膜和缺测处理均有记录
- 训练与验证时空块互斥并防止目标泄漏
- 预处理后的时间轴、坐标、单位和形状可检查

## 可调资源（edge:resource，仅真实存在）
- datasets/ERA5

## 实例任务（本骨架在各场景的实例化）
- it-13c7f7ad
- it-1bb1168d
- it-4165cff6
- it-c8d81770
- it-de8ac596
- it-e6aedb32
- it-e97774c7

## 复用场景
- E38
- E53
- E93
- E89
- E40
- E15
- E55
