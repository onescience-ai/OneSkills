# 实例任务：水文强迫和流域资料及任务边界预检 @ E16

- domain: climate
- 骨架: climate-hydro-forcing-basin-data-boundary-precheck-task
- 场景: climate-remote-sensing-soil-moisture-kilometer-scale-spatial-scenario (E16)
- step_id: s01
- depend: []

## 场景研究主体
- E16
- 关联论文: Global downscaling of remotely sensed soil moisture using neural networks | doi:; Global long term daily 1 km surface soil moisture dataset with physics informed machine learning | doi:; Global soil moisture data derived through machine learning trained with in-situ measurements | doi:

## 本实例步骤描述
界定“遥感土壤湿度公里级空间降尺度与时序重建”的任务范围并执行“水文强迫和流域资料及任务边界预检”，核验卫星土壤湿度、植被地表温度、地形土壤属性的来源、覆盖、有效时间和可用边界。

## 本实例执行 prompt
面向“遥感土壤湿度公里级空间降尺度与时序重建”，读取{COARSE_SOIL_MOISTURE}、{FINE_SCALE_COVARIATES}、{FINE_REFERENCE}、{GAP_MASK}、{TARGET_GRID}并完成水文强迫和流域资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。

## 本实例输入槽
- {COARSE_SOIL_MOISTURE} | required=True | type=str | var_name=粗网格土壤湿度 | hint=输入粗网格土壤湿度。 | default=None
- {FINE_SCALE_COVARIATES} | required=True | type=str | var_name=细尺度辅助变量 | hint=输入地表地形辅助资料。 | default=None
- {FINE_REFERENCE} | required=True | type=str | var_name=细尺度参考资料 | hint=输入细尺度参考路径。 | default=None
- {GAP_MASK} | required=False | type=str | var_name=时间缺口掩膜 | hint=输入时间缺口掩膜。 | default=None
- {TARGET_GRID} | required=True | type=str | var_name=公里级目标网格 | hint=输入公里级网格规格。 | default=None

## 本实例产出
- 输入数据与版本清单
- 任务范围和资料截止时间表
- 输入完整性预检报告

## 本实例质量门禁
- 所有必需输入均存在且路径、版本和来源可追溯
- 任务区域、时段、变量和输出目标无歧义
- 缺测、重复和异常资料已记录且未擅自补造
- 气象强迫、流域边界和水文观测时空一致
- 粗网格土壤湿度、细尺度参考和缺口掩膜分别登记

## 可调资源（edge:resource，仅真实存在）
- datasets/international-soil-moisture-network-ismn
- datasets/ismn-and-nasa-power-datasets-for-soil-moisture-prediction
- datasets/smap-level-3-passive-soil-moisture-products
- models/neural-network-soil-moisture-downscaling

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
