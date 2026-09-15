# 实例任务：海洋状态和强迫资料及任务边界预检 @ E29

- domain: climate
- 骨架: tk-climate-2239ace0
- 场景: sc-dfcf58f9 (E29)
- step_id: s01
- depend: []

## 场景研究主体
- E29
- 关联论文: CAS-Canglong- A skillful 3D Transformer model for sub-seasonal to seasonal global sea surface temperature prediction | doi:; A deep learning model for forecasting global monthly mean sea surface temperature anomalies | doi:; Multi-Dilated Convolutional LSTM With U-Net for Global Sea Surface Temperature Forecasting | doi:

## 本实例步骤描述
界定“全球海表温度次季节—季节异常预报”的任务范围并执行“海洋状态和强迫资料及任务边界预检”，核验历史海温、海洋状态和遥相关前兆的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“全球海表温度次季节—季节异常预报”，读取{OCEAN_STATE}、{SURFACE_FORCING}、{STATIC_OCEAN_DATA}、{START_TIME}、{TARGET_HORIZON}、{DATA_CUTOFF_TIME}并完成海洋状态和强迫资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {OCEAN_STATE} | required=True | type=str | var_name=海洋状态资料 | hint=输入海洋状态资料路径。 | default=None
- {SURFACE_FORCING} | required=False | type=str | var_name=海表强迫资料 | hint=输入海表强迫资料路径。 | default=None
- {STATIC_OCEAN_DATA} | required=False | type=str | var_name=静态海洋资料 | hint=输入地形掩膜等资料。 | default=None
- {START_TIME} | required=True | type=str | var_name=起始时刻 | hint=输入处理起始时刻。 | default=None
- {TARGET_HORIZON} | required=True | type=str | var_name=目标时效 | hint=输入目标时效或时段。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 海陆掩膜、岸线、垂向层和海洋单位一致

## 可调资源（edge:resource，仅真实存在）
- datasets/CMEMS

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
