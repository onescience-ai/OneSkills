# 骨架任务：遥感观测标签及任务边界预检

- domain: climate
- 复用场景数: 16
- 实例任务数: 16

## 步骤描述（跨场景聚合去重）
- 界定“30米大范围农田范围与面积制图”的任务范围并执行“遥感观测标签及任务边界预检”，核验多季节Landsat影像、植被指数和训练样本的来源、覆盖、有效时间和可用边界。
- 界定“IASI近实时大气氨柱浓度反演”的任务范围并执行“遥感观测标签及任务边界预检”，核验IASI红外光谱、热力廓线和观测几何的来源、覆盖、有效时间和可用边界。
- 界定“Landsat水体叶绿素a概率反演”的任务范围并执行“遥感观测标签及任务边界预检”，核验Landsat水色波段、观测几何和水样叶绿素标签的来源、覆盖、有效时间和可用边界。
- 界定“OCO-2驱动区域人为二氧化碳排放反演”的任务范围并执行“遥感观测标签及任务边界预检”，核验OCO-2柱浓度、气象输送和人类活动代理的来源、覆盖、有效时间和可用边界。
- 界定“光学影像岩石冰川目标提取与矢量清查”的任务范围并执行“遥感观测标签及任务边界预检”，核验光学卫星影像、DEM和人工样本的来源、覆盖、有效时间和可用边界。
- 界定“全球10米近实时土地覆盖制图”的任务范围并执行“遥感观测标签及任务边界预检”，核验多时相光学卫星影像、辅助地理信息和标签的来源、覆盖、有效时间和可用边界。
- 界定“全球高分辨率树冠高度制图”的任务范围并执行“遥感观测标签及任务边界预检”，核验多光谱卫星影像、激光测高样本和地形的来源、覆盖、有效时间和可用边界。
- 界定“可见光影像云掩膜与云不透明度分类”的任务范围并执行“遥感观测标签及任务边界预检”，核验多光谱或RGB影像、观测几何和清空参考的来源、覆盖、有效时间和可用边界。
- 界定“土壤高光谱反射率驱动有机碳含量反演”的任务范围并执行“遥感观测标签及任务边界预检”，核验土壤高光谱反射率、样品SOC和观测条件的来源、覆盖、有效时间和可用边界。
- 界定“多源遥感南极冰架表面融化识别”的任务范围并执行“遥感观测标签及任务边界预检”，核验光学、微波等遥感序列及冰架掩膜的来源、覆盖、有效时间和可用边界。
- 界定“无人机激光雷达—影像森林结构与碳储量估计”的任务范围并执行“遥感观测标签及任务边界预检”，核验无人机点云或RGB影像、样地清查和异速生长关系的来源、覆盖、有效时间和可用边界。
- 界定“草地地上生物量遥感估计与气候响应诊断”的任务范围并执行“遥感观测标签及任务边界预检”，核验多源遥感、气象、地形和样地生物量的来源、覆盖、有效时间和可用边界。
- 界定“被动微波卫星瞬时降水率反演”的任务范围并执行“遥感观测标签及任务边界预检”，核验多通道微波亮温、扫描几何和环境辅助量的来源、覆盖、有效时间和可用边界。
- 界定“遥感—气象耦合植被物候日期估计”的任务范围并执行“遥感观测标签及任务边界预检”，核验植被指数、气象累计量、雪盖、地形和物候观测的来源、覆盖、有效时间和可用边界。
- 界定“静止卫星卷云覆盖与光学属性反演”的任务范围并执行“遥感观测标签及任务边界预检”，核验静止卫星多光谱辐亮度、观测几何和辅助大气场的来源、覆盖、有效时间和可用边界。
- 界定“高光谱卫星甲烷羽流像素级检测”的任务范围并执行“遥感观测标签及任务边界预检”，核验高光谱辐亮度、背景场和羽流标签的来源、覆盖、有效时间和可用边界。

## 执行 prompt（跨场景聚合去重）
- 面向“30米大范围农田范围与面积制图”，读取{SENSOR_DATA}、{AUXILIARY_DATA}、{TARGET_REGION_TIME}、{REFERENCE_LABELS}、{QUALITY_MASK}并完成遥感观测标签及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“IASI近实时大气氨柱浓度反演”，读取{SENSOR_DATA}、{AUXILIARY_DATA}、{TARGET_REGION_TIME}、{REFERENCE_LABELS}、{QUALITY_MASK}并完成遥感观测标签及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“Landsat水体叶绿素a概率反演”，读取{SENSOR_DATA}、{AUXILIARY_DATA}、{TARGET_REGION_TIME}、{REFERENCE_LABELS}、{QUALITY_MASK}并完成遥感观测标签及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“OCO-2驱动区域人为二氧化碳排放反演”，读取{SENSOR_DATA}、{AUXILIARY_DATA}、{TARGET_REGION_TIME}、{REFERENCE_LABELS}、{QUALITY_MASK}并完成遥感观测标签及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“光学影像岩石冰川目标提取与矢量清查”，读取{SENSOR_DATA}、{AUXILIARY_DATA}、{TARGET_REGION_TIME}、{REFERENCE_LABELS}、{QUALITY_MASK}并完成遥感观测标签及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“全球10米近实时土地覆盖制图”，读取{SENSOR_DATA}、{AUXILIARY_DATA}、{TARGET_REGION_TIME}、{REFERENCE_LABELS}、{QUALITY_MASK}并完成遥感观测标签及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“全球高分辨率树冠高度制图”，读取{SENSOR_DATA}、{AUXILIARY_DATA}、{TARGET_REGION_TIME}、{REFERENCE_LABELS}、{QUALITY_MASK}并完成遥感观测标签及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“可见光影像云掩膜与云不透明度分类”，读取{SENSOR_DATA}、{AUXILIARY_DATA}、{TARGET_REGION_TIME}、{REFERENCE_LABELS}、{QUALITY_MASK}并完成遥感观测标签及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“土壤高光谱反射率驱动有机碳含量反演”，读取{SENSOR_DATA}、{AUXILIARY_DATA}、{TARGET_REGION_TIME}、{REFERENCE_LABELS}、{QUALITY_MASK}并完成遥感观测标签及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“多源遥感南极冰架表面融化识别”，读取{SENSOR_DATA}、{AUXILIARY_DATA}、{TARGET_REGION_TIME}、{REFERENCE_LABELS}、{QUALITY_MASK}并完成遥感观测标签及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“无人机激光雷达—影像森林结构与碳储量估计”，读取{SENSOR_DATA}、{AUXILIARY_DATA}、{TARGET_REGION_TIME}、{REFERENCE_LABELS}、{QUALITY_MASK}并完成遥感观测标签及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“草地地上生物量遥感估计与气候响应诊断”，读取{SENSOR_DATA}、{AUXILIARY_DATA}、{TARGET_REGION_TIME}、{REFERENCE_LABELS}、{QUALITY_MASK}并完成遥感观测标签及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“被动微波卫星瞬时降水率反演”，读取{SENSOR_DATA}、{AUXILIARY_DATA}、{TARGET_REGION_TIME}、{REFERENCE_LABELS}、{QUALITY_MASK}并完成遥感观测标签及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“遥感—气象耦合植被物候日期估计”，读取{SENSOR_DATA}、{AUXILIARY_DATA}、{TARGET_REGION_TIME}、{REFERENCE_LABELS}、{QUALITY_MASK}并完成遥感观测标签及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“静止卫星卷云覆盖与光学属性反演”，读取{SENSOR_DATA}、{AUXILIARY_DATA}、{TARGET_REGION_TIME}、{REFERENCE_LABELS}、{QUALITY_MASK}并完成遥感观测标签及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“高光谱卫星甲烷羽流像素级检测”，读取{SENSOR_DATA}、{AUXILIARY_DATA}、{TARGET_REGION_TIME}、{REFERENCE_LABELS}、{QUALITY_MASK}并完成遥感观测标签及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 输入槽（var/hint/default）
- {SENSOR_DATA} | required=True | type=str | var_name=传感器观测 | hint=输入传感器观测路径。 | default=None
- {AUXILIARY_DATA} | required=False | type=str | var_name=辅助资料 | hint=输入辅助资料路径。 | default=None
- {TARGET_REGION_TIME} | required=True | type=str | var_name=目标区域时段 | hint=输入区域和观测时段。 | default=None
- {REFERENCE_LABELS} | required=False | type=str | var_name=参考标签资料 | hint=输入参考标签路径。 | default=None
- {QUALITY_MASK} | required=False | type=str | var_name=质量掩膜 | hint=输入质量掩膜路径。 | default=None

## 产出
- 任务范围和资料截止时间表
- 输入完整性预检报告
- 输入数据与版本清单

## 质量门禁 quality_gate
- 任务区域、时段、变量和输出目标无歧义
- 传感器、轨道、处理级别和观测时间可追溯
- 所有必需输入均存在且路径、版本和来源可追溯
- 标签采用互斥多类土地覆盖体系而非农田二分类
- 标签限定为农田二分类并明确最小制图单元
- 缺测、重复和异常资料已记录且未擅自补造

## 可调资源（edge:resource，仅真实存在）
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/gleam-v3-8a-global-land-evaporation-dataset
- datasets/ostia-sst-data
- datasets/snodas-swe-data-product
- datasets/south-korea-air-quality-and-weather-monitoring-dataset
- models/dynamic-pre-training-for-time-series-dynpt
- models/multivariate-data-fusion-vector-wind-prediction

## 实例任务（本骨架在各场景的实例化）
- climate-remote-sensing-label-and-30m-large-scale-farmland-inst
- climate-remote-sensing-label-and-geostationary-satellite-inst
- climate-remote-sensing-label-and-global-10m-near-real-time-inst
- climate-remote-sensing-label-and-global-high-resolution-inst
- climate-remote-sensing-label-and-grassland-aboveground-inst
- climate-remote-sensing-label-and-hyperspectral-satellite-inst
- climate-remote-sensing-label-and-iasi-near-real-time-atmosphe-inst
- climate-remote-sensing-label-and-landsat-water-chlorophyll-a-inst
- climate-remote-sensing-label-and-multi-source-remote-sensing-inst
- climate-remote-sensing-label-and-oco-2-regional-anthropogenic-inst
- climate-remote-sensing-label-and-optical-imagery-rock-glacier-inst
- climate-remote-sensing-label-and-passive-microwave-satellite-inst
- climate-remote-sensing-label-and-remote-sensing-meteorologica-inst
- climate-remote-sensing-label-and-soil-hyperspectral-reflectan-inst
- climate-remote-sensing-label-and-uav-lidar-image-forest-inst
- climate-remote-sensing-label-and-visible-image-cloud-mask-inst

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
