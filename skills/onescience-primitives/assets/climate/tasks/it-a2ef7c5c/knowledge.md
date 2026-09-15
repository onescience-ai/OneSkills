# 实例任务：目标序列及缺口及任务边界预检 @ E49

- domain: climate
- 骨架: tk-climate-6267ea98
- 场景: sc-3b456843 (E49)
- step_id: s01
- depend: []

## 场景研究主体
- E49
- 关联论文: GTWS-MLrec- global terrestrial water storage reconstruction by machine learning from 1940 to present | doi:; Global high-resolution total water storage anomalies from self-supervised data assimilation using deep learning algorithms | doi:

## 本实例步骤描述
界定“GRACE缺测期全球陆地水储量异常重建”的任务范围并执行“目标序列及缺口及任务边界预检”，核验GRACE观测、气候驱动、陆面状态的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“GRACE缺测期全球陆地水储量异常重建”，读取{GRACE_TWSA_SERIES}、{CLIMATE_LAND_DRIVERS}、{GAP_MASK}、{REFERENCE_PERIOD}、{TARGET_GRID}并完成目标序列及缺口及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {GRACE_TWSA_SERIES} | required=True | type=str | var_name=GRACE水储量序列 | hint=输入GRACE水储量路径。 | default=None
- {CLIMATE_LAND_DRIVERS} | required=True | type=str | var_name=气候陆面驱动 | hint=输入气候陆面资料路径。 | default=None
- {GAP_MASK} | required=True | type=str | var_name=GRACE缺口掩膜 | hint=输入GRACE缺口掩膜。 | default=None
- {REFERENCE_PERIOD} | required=True | type=str | var_name=异常基准期 | hint=输入异常基准时段。 | default=None
- {TARGET_GRID} | required=True | type=str | var_name=目标网格 | hint=输入目标网格规格。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 目标序列、辅助资料和真实缺口掩膜可追溯
- GRACE水储量序列、异常基准期和真实缺口明确

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
