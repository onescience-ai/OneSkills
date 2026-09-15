# 骨架任务：情景外强迫及任务边界预检

- domain: climate
- 复用场景数: 2
- 实例任务数: 2

## 步骤描述（跨场景聚合去重）
- 界定“给定边界强迫的全球大气气候轨迹代理模拟”的任务范围并执行“情景外强迫及任务边界预检”，核验海温、太阳辐射、地形及初始大气状态的来源、覆盖、有效时间和可用边界。
- 界定“给定边界强迫的全球气候大集合生成”的任务范围并执行“情景外强迫及任务边界预检”，核验外部强迫、边界条件、随机种子和初始状态的来源、覆盖、有效时间和可用边界。

## 执行 prompt（跨场景聚合去重）
- 面向“给定边界强迫的全球大气气候轨迹代理模拟”，读取{BOUNDARY_FORCING}、{SCENARIO_DEFINITION}、{SIMULATION_PERIOD}、{REFERENCE_PERIOD}并完成情景外强迫及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- 面向“给定边界强迫的全球气候大集合生成”，读取{BOUNDARY_FORCING}、{SCENARIO_DEFINITION}、{SIMULATION_PERIOD}、{REFERENCE_PERIOD}并完成情景外强迫及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 输入槽（var/hint/default）
- {BOUNDARY_FORCING} | required=True | type=str | var_name=边界与外强迫 | hint=输入边界和强迫资料路径。 | default=None
- {SCENARIO_DEFINITION} | required=True | type=str | var_name=情景定义 | hint=输入气候情景定义。 | default=None
- {SIMULATION_PERIOD} | required=True | type=str | var_name=模拟时段 | hint=输入模拟起止时间。 | default=None
- {REFERENCE_PERIOD} | required=True | type=str | var_name=异常基准期 | hint=输入异常基准时段。 | default=None

## 产出
- 任务范围和资料截止时间表
- 输入完整性预检报告
- 输入数据与版本清单

## 质量门禁 quality_gate
- 任务区域、时段、变量和输出目标无歧义
- 外强迫、情景、日历和基准期定义可追溯
- 所有必需输入均存在且路径、版本和来源可追溯
- 缺测、重复和异常资料已记录且未擅自补造

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- it-12e33219
- it-c0a1ffe3

## 复用场景
- E57
- E36
