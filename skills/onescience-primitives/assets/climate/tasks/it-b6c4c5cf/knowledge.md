# 实例任务：遥感观测标签及任务边界预检 @ E77

- domain: climate
- 骨架: tk-climate-c9ed671b
- 场景: sc-4f5071fd (E77)
- step_id: s01
- depend: []

## 场景研究主体
- E77
- 关联论文: Automated detection of rock glaciers using deep learning and object-based image analysis | doi:

## 本实例步骤描述
界定“光学影像岩石冰川目标提取与矢量清查”的任务范围并执行“遥感观测标签及任务边界预检”，核验光学卫星影像、DEM和人工样本的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“光学影像岩石冰川目标提取与矢量清查”，读取{SENSOR_DATA}、{AUXILIARY_DATA}、{TARGET_REGION_TIME}、{REFERENCE_LABELS}、{QUALITY_MASK}并完成遥感观测标签及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {SENSOR_DATA} | required=True | type=str | var_name=传感器观测 | hint=输入传感器观测路径。 | default=None
- {AUXILIARY_DATA} | required=False | type=str | var_name=辅助资料 | hint=输入辅助资料路径。 | default=None
- {TARGET_REGION_TIME} | required=True | type=str | var_name=目标区域时段 | hint=输入区域和观测时段。 | default=None
- {REFERENCE_LABELS} | required=False | type=str | var_name=参考标签资料 | hint=输入参考标签路径。 | default=None
- {QUALITY_MASK} | required=False | type=str | var_name=质量掩膜 | hint=输入质量掩膜路径。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 传感器、轨道、处理级别和观测时间可追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
