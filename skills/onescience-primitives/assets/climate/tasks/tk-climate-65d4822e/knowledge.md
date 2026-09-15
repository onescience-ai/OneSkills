# 骨架任务：观测和背景场及任务边界预检

- domain: climate
- 复用场景数: 2
- 实例任务数: 2

## 步骤描述（跨场景聚合去重）
- 界定“多源原始观测驱动的全球分析—预报闭环”的任务范围并执行“观测和背景场及任务边界预检”，核验带时间和位置的原始观测、背景状态的来源、覆盖、有效时间和可用边界。
- 界定“稀疏观测三维温盐场快速重建与同化初始化”的任务范围并执行“观测和背景场及任务边界预检”，核验稀疏温盐剖面、卫星表层观测和背景场的来源、覆盖、有效时间和可用边界。

## 执行 prompt（跨场景聚合去重）
- 面向“多源原始观测驱动的全球分析—预报闭环”，读取{OBSERVATION_DATA}、{BACKGROUND_STATE}、{ANALYSIS_TIME}、{ASSIMILATION_WINDOW}、{DATA_CUTOFF_TIME}并完成观测和背景场及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“稀疏观测三维温盐场快速重建与同化初始化”，读取{OBSERVATION_DATA}、{BACKGROUND_STATE}、{ANALYSIS_TIME}、{ASSIMILATION_WINDOW}、{DATA_CUTOFF_TIME}并完成观测和背景场及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 输入槽（var/hint/default）
- {OBSERVATION_DATA} | required=True | type=str | var_name=原始观测资料 | hint=输入原始观测资料路径。 | default=None
- {BACKGROUND_STATE} | required=True | type=str | var_name=背景状态 | hint=输入背景状态路径。 | default=None
- {ANALYSIS_TIME} | required=True | type=str | var_name=分析时刻 | hint=输入目标分析时刻。 | default=None
- {ASSIMILATION_WINDOW} | required=True | type=str | var_name=同化时间窗 | hint=输入同化时间窗。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 产出
- 任务范围和资料截止时间表
- 输入完整性预检报告
- 输入数据与版本清单

## 质量门禁 quality_gate
- 任务区域、时段、变量和输出目标无歧义
- 所有必需输入均存在且路径、版本和来源可追溯
- 缺测、重复和异常资料已记录且未擅自补造
- 观测可用时间、质控标志和误差配置可追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-b7445df4
- it-f22415f8

## 复用场景
- E4
- E48
