# 实例任务：粗细分辨率资料及任务边界预检 @ E53

- domain: climate
- 骨架: tk-climate-721f3e3f
- 场景: sc-a5021c3d (E53)
- step_id: s01
- depend: []

## 场景研究主体
- E53
- 关联论文: A Deep Learning Method for Bias Correction of ECMWF 24–240 h Forecasts | doi:; ECMWF short-term prediction accuracy improvement by deep learning | doi:

## 本实例步骤描述
界定“NWP 24—240小时近地面多变量偏差订正”的任务范围并执行“粗细分辨率资料及任务边界预检”，核验原始NWP预报、起报分析、历史验证资料的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“NWP 24—240小时近地面多变量偏差订正”，读取{COARSE_INPUT}、{FINE_REFERENCE}、{TARGET_GRID}、{ANALYSIS_PERIOD}、{DATA_CUTOFF_TIME}并完成粗细分辨率资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {COARSE_INPUT} | required=True | type=str | var_name=粗分辨率输入 | hint=输入粗分辨率资料路径。 | default=None
- {FINE_REFERENCE} | required=True | type=str | var_name=高分辨率参考 | hint=输入高分辨率参考路径。 | default=None
- {TARGET_GRID} | required=True | type=str | var_name=目标网格 | hint=输入目标网格规格。 | default=None
- {ANALYSIS_PERIOD} | required=True | type=str | var_name=处理时段 | hint=输入处理起止时间。 | default=None
- {DATA_CUTOFF_TIME} | required=True | type=str | var_name=资料截止时间 | hint=输入资料截止时间。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 粗细分辨率样本严格同期且坐标一致

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
