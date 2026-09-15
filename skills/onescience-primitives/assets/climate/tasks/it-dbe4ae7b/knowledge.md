# 实例任务：天气能源运行资料时空对齐与样本构造 @ E26

- domain: climate
- 骨架: tk-climate-f01f7781
- 场景: sc-2528a6c2 (E26)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- E26
- 关联论文: A machine learning model for hub-height short-term wind speed prediction | doi:; Estimating hub-height wind speed based on a machine learning algorithm- implications for wind energy assessment | doi:; Terrain-aware Deep Learning for Wind Energy Applications- From Kilometer-scale Forecasts to Fine Wind Fields | doi:; The importance of round-robin validation when assessing machine-learning-based vertical extrapolation of wind speeds | doi:

## 本实例步骤描述
执行“天气能源运行资料时空对齐与样本构造”，统一近地面风、NWP、地形、轮毂高度的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 本实例执行 prompt
依据{TERRAIN_ALIGNMENT_CONFIG}、{VERTICAL_MAPPING_CONFIG}、{MISSING_VALUE_POLICY}完成天气能源运行资料时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 本实例输入槽
- {TERRAIN_ALIGNMENT_CONFIG} | required=True | type=str | var_name=地形对齐配置 | hint=输入地形对齐配置。 | default=None
- {VERTICAL_MAPPING_CONFIG} | required=True | type=str | var_name=垂向映射配置 | hint=输入轮毂高度映射配置。 | default=None
- {MISSING_VALUE_POLICY} | required=True | type=str | var_name=缺测处理规则 | hint=输入缺测处理规则。 | default=None

## 本实例产出
- 对齐后的标准输入
- 掩膜与样本索引
- 预处理转换记录

## 本实例质量门禁
- 预处理后的时间轴、坐标、单位和形状可检查
- 每项插值、归一化、掩膜和缺测处理均有记录
- 不存在由验证资料或未来资料造成的信息泄漏
- 容量、时区、采样间隔和缺测规则一致

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
