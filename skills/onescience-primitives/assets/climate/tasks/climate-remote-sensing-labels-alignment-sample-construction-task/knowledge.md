# 骨架任务：遥感观测标签时空对齐与样本构造

- domain: climate
- 复用场景数: 16
- 实例任务数: 16

## 步骤描述（跨场景聚合去重）
- 执行“遥感观测标签时空对齐与样本构造”，统一IASI红外光谱、热力廓线和观测几何的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“遥感观测标签时空对齐与样本构造”，统一Landsat水色波段、观测几何和水样叶绿素标签的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“遥感观测标签时空对齐与样本构造”，统一OCO-2柱浓度、气象输送和人类活动代理的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“遥感观测标签时空对齐与样本构造”，统一光学、微波等遥感序列及冰架掩膜的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“遥感观测标签时空对齐与样本构造”，统一光学卫星影像、DEM和人工样本的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“遥感观测标签时空对齐与样本构造”，统一土壤高光谱反射率、样品SOC和观测条件的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“遥感观测标签时空对齐与样本构造”，统一多光谱卫星影像、激光测高样本和地形的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“遥感观测标签时空对齐与样本构造”，统一多光谱或RGB影像、观测几何和清空参考的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“遥感观测标签时空对齐与样本构造”，统一多季节Landsat影像、植被指数和训练样本的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“遥感观测标签时空对齐与样本构造”，统一多时相光学卫星影像、辅助地理信息和标签的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“遥感观测标签时空对齐与样本构造”，统一多源遥感、气象、地形和样地生物量的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“遥感观测标签时空对齐与样本构造”，统一多通道微波亮温、扫描几何和环境辅助量的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“遥感观测标签时空对齐与样本构造”，统一无人机点云或RGB影像、样地清查和异速生长关系的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“遥感观测标签时空对齐与样本构造”，统一植被指数、气象累计量、雪盖、地形和物候观测的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“遥感观测标签时空对齐与样本构造”，统一静止卫星多光谱辐亮度、观测几何和辅助大气场的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“遥感观测标签时空对齐与样本构造”，统一高光谱辐亮度、背景场和羽流标签的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 执行 prompt（跨场景聚合去重）
- 依据{CALIBRATION_CONFIG}、{COREGISTRATION_CONFIG}、{TILE_CONFIG}完成遥感观测标签时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 输入槽（var/hint/default）
- {CALIBRATION_CONFIG} | required=True | type=str | var_name=辐射定标配置 | hint=输入定标配置。 | default=None
- {COREGISTRATION_CONFIG} | required=True | type=str | var_name=几何配准配置 | hint=输入几何配准配置。 | default=None
- {TILE_CONFIG} | required=True | type=str | var_name=切片配置 | hint=输入切片和重叠配置。 | default=None

## 产出
- 对齐后的标准输入
- 掩膜与样本索引
- 预处理转换记录

## 质量门禁 quality_gate
- 不存在由验证资料或未来资料造成的信息泄漏
- 每项插值、归一化、掩膜和缺测处理均有记录
- 辐射定标、几何配准和质量掩膜均有记录
- 预处理后的时间轴、坐标、单位和形状可检查

## 可调资源（edge:resource，仅真实存在）
- datasets/gleam-v3-8a-global-land-evaporation-dataset
- models/neural-network-based-nwp-model-calibration

## 实例任务（本骨架在各场景的实例化）
- climate-remote-sensing-labels-30m-large-scale-farmland-inst
- climate-remote-sensing-labels-geostationary-satellite-inst
- climate-remote-sensing-labels-global-10m-near-real-time-inst
- climate-remote-sensing-labels-global-high-resolution-inst
- climate-remote-sensing-labels-grassland-aboveground-inst
- climate-remote-sensing-labels-hyperspectral-satellite-inst
- climate-remote-sensing-labels-iasi-near-real-time-atmosphe-inst
- climate-remote-sensing-labels-landsat-water-chlorophyll-a-inst
- climate-remote-sensing-labels-multi-source-remote-sensing-inst
- climate-remote-sensing-labels-oco-2-regional-anthropogenic-inst
- climate-remote-sensing-labels-optical-imagery-rock-glacier-inst
- climate-remote-sensing-labels-passive-microwave-satellite-inst
- climate-remote-sensing-labels-remote-sensing-meteorologica-inst
- climate-remote-sensing-labels-soil-hyperspectral-reflectan-inst
- climate-remote-sensing-labels-uav-lidar-image-forest-inst
- climate-remote-sensing-labels-visible-image-cloud-mask-inst

## 复用场景
- E56
- E79
- E73
- E84
- E77
- E71
- E86
- E35
- E68
- E75
- E59
- E96
- E12
- E67
- E54
- E81
