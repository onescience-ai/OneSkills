# 实例任务：致灾因子和事件标签及任务边界预检 @ E90

- domain: climate
- 骨架: tk-climate-227e3d3b
- 场景: sc-ddd58d0f (E90)
- step_id: s01
- depend: []

## 场景研究主体
- E90
- 关联论文: Early forecasting of tsunami inundation from tsunami and geodetic observation data with convolutional neural networks | doi:

## 本实例步骤描述
界定“海啸与大地测量观测驱动的快速淹没范围预报”的任务范围并执行“致灾因子和事件标签及任务边界预检”，核验海啸浮标、海平面与地壳形变观测的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“海啸与大地测量观测驱动的快速淹没范围预报”，读取{HAZARD_DRIVERS}、{STATIC_CONDITIONS}、{EVENT_LABELS}、{TARGET_WINDOW}、{DATA_CUTOFF_TIME}并完成致灾因子和事件标签及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {HAZARD_DRIVERS} | required=True | type=str | var_name=致灾驱动资料 | hint=输入致灾驱动资料路径。 | default=None
- {STATIC_CONDITIONS} | required=False | type=str | var_name=静态环境资料 | hint=输入地形和下垫面资料。 | default=None
- {EVENT_LABELS} | required=True | type=str | var_name=历史事件标签 | hint=输入历史事件标签路径。 | default=None
- {TARGET_WINDOW} | required=True | type=str | var_name=目标预警窗口 | hint=输入目标预警时间窗。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 事件定义、预警窗口和资料截止时间明确

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
