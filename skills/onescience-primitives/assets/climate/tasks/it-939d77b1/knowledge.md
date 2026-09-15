# 实例任务：观测和背景场时空对齐与样本构造 @ E4

- domain: climate
- 骨架: tk-climate-11037b61
- 场景: sc-84809286 (E4)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- E4
- 关联论文: A data-to-forecast machine learning system for global weather | doi:; End-to-end data-driven weather prediction | doi:; GraphDOP_ Towards skilful data-driven medium-range weather forecasts learnt and initialised directly from observations | doi:

## 本实例步骤描述
执行“观测和背景场时空对齐与样本构造”，统一带时间和位置的原始观测、背景状态的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

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
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
