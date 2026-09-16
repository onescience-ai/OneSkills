# 实例任务：观测和背景场时空对齐与样本构造 @ E48

- domain: climate
- 骨架: climate-observation-background-field-alignment-and-sampling-task
- 场景: climate-sparse-observation-3d-temperature-salt-field-fast-scenario (E48)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- E48
- 关联论文: Rapid reconstruction of temperature and salinity fields based on machine learning and the assimilation application | doi:; Super-resolution data assimilation | doi:

## 本实例步骤描述
执行“观测和背景场时空对齐与样本构造”，统一稀疏温盐剖面、卫星表层观测和背景场的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 本实例执行 prompt
依据{OBSERVATION_QC}、{OBSERVATION_ERRORS}、{TARGET_GRID}完成观测和背景场时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 本实例输入槽
- {OBSERVATION_QC} | required=True | type=str | var_name=观测质控配置 | hint=输入观测质控配置。 | default=None
- {OBSERVATION_ERRORS} | required=True | type=str | var_name=观测误差配置 | hint=输入观测误差配置。 | default=None
- {TARGET_GRID} | required=True | type=str | var_name=分析网格 | hint=输入分析网格规格。 | default=None

## 本实例产出
- 对齐后的标准输入
- 掩膜与样本索引
- 预处理转换记录

## 本实例质量门禁
- 预处理后的时间轴、坐标、单位和形状可检查
- 每项插值、归一化、掩膜和缺测处理均有记录
- 不存在由验证资料或未来资料造成的信息泄漏
- 背景场与观测在时空位置和物理量上匹配

## 可调资源（edge:resource，仅真实存在）
- datasets/lpma-airport-wind-observation-validation

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
