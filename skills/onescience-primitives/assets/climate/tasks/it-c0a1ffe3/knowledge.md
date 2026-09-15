# 实例任务：情景外强迫及任务边界预检 @ E57

- domain: climate
- 骨架: tk-climate-a40fd40a
- 场景: sc-f46bfa08 (E57)
- step_id: s01
- depend: []

## 场景研究主体
- E57
- 关联论文: ACE_ A fast, skillful learned global atmospheric model for climate prediction | doi:; Neural general circulation models for weather and climate | doi:

## 本实例步骤描述
界定“给定边界强迫的全球大气气候轨迹代理模拟”的任务范围并执行“情景外强迫及任务边界预检”，核验海温、太阳辐射、地形及初始大气状态的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“给定边界强迫的全球大气气候轨迹代理模拟”，读取{BOUNDARY_FORCING}、{SCENARIO_DEFINITION}、{SIMULATION_PERIOD}、{REFERENCE_PERIOD}并完成情景外强迫及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {BOUNDARY_FORCING} | required=True | type=str | var_name=边界与外强迫 | hint=输入边界和强迫资料路径。 | default=None
- {SCENARIO_DEFINITION} | required=True | type=str | var_name=情景定义 | hint=输入气候情景定义。 | default=None
- {SIMULATION_PERIOD} | required=True | type=str | var_name=模拟时段 | hint=输入模拟起止时间。 | default=None
- {REFERENCE_PERIOD} | required=True | type=str | var_name=异常基准期 | hint=输入异常基准时段。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 外强迫、情景、日历和基准期定义可追溯

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
