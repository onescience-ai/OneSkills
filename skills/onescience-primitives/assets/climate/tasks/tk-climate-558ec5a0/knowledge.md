# 骨架任务：源观测和参考资料时空对齐与样本构造

- domain: climate
- 复用场景数: 6
- 实例任务数: 6

## 步骤描述（跨场景聚合去重）
- 执行“源观测和参考资料时空对齐与样本构造”，统一多时次多光谱卫星云图、对流初生标签的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“源观测和参考资料时空对齐与样本构造”，统一激光雷达后向散射剖面、探空、地面气象的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“源观测和参考资料时空对齐与样本构造”，统一站点日温度、湿度、风速及可选时间特征的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“源观测和参考资料时空对齐与样本构造”，统一表面温湿压风分析场、人工锋面标签的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“源观测和参考资料时空对齐与样本构造”，统一雷达多仰角反射率、雨量计观测、质量标识的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“源观测和参考资料时空对齐与样本构造”，统一雷达观测、卫星云图、雨量计及地理特征的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 执行 prompt（跨场景聚合去重）
- 依据{ALIGNMENT_CONFIG}、{QUALITY_CONTROL}、{REFERENCE_DEFINITION}完成源观测和参考资料时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。
- 依据{COREGISTRATION_CONFIG}、{GAUGE_QC}、{FUSION_GRID}完成源观测和参考资料时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。
- 依据{RADAR_QC}、{VERTICAL_FEATURE_CONFIG}、{TARGET_GRID}完成源观测和参考资料时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 输入槽（var/hint/default）
- {ALIGNMENT_CONFIG} | required=True | type=str | var_name=时空对齐配置 | hint=输入时空对齐配置。 | default=None
- {QUALITY_CONTROL} | required=True | type=str | var_name=质量控制配置 | hint=输入质量控制配置。 | default=None
- {REFERENCE_DEFINITION} | required=False | type=str | var_name=参考定义 | hint=输入标签或参考定义。 | default=None
- {RADAR_QC} | required=True | type=str | var_name=雷达质控配置 | hint=输入雷达质控配置。 | default=None
- {VERTICAL_FEATURE_CONFIG} | required=True | type=str | var_name=垂直特征配置 | hint=输入体扫特征配置。 | default=None
- {TARGET_GRID} | required=True | type=str | var_name=雷达目标网格 | hint=输入雷达目标网格。 | default=None
- {COREGISTRATION_CONFIG} | required=True | type=str | var_name=多模态配准 | hint=输入多模态配准配置。 | default=None
- {GAUGE_QC} | required=True | type=str | var_name=雨量计质控 | hint=输入雨量计质控配置。 | default=None
- {FUSION_GRID} | required=True | type=str | var_name=融合目标网格 | hint=输入融合目标网格。 | default=None

## 产出
- 对齐后的标准输入
- 掩膜与样本索引
- 预处理转换记录

## 质量门禁 quality_gate
- 不存在由验证资料或未来资料造成的信息泄漏
- 同期资料在坐标、单位和质量标志上严格对齐
- 每项插值、归一化、掩膜和缺测处理均有记录
- 预处理后的时间轴、坐标、单位和形状可检查

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-20aa4690
- it-27dc2381
- it-3b4e6cca
- it-7e716537
- it-abbd38f5
- it-c44845be

## 复用场景
- E63
- E97
- E34
- E61
- E21
- E80
