# 实例任务：海洋状态和强迫资料时空对齐与样本构造 @ E17

- domain: climate
- 骨架: climate-ocean-state-forcing-stalign-sample-task
- 场景: climate-arctic-sea-ice-jantojune-probabilistic-forecast-scenario (E17)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- E17
- 关联论文: Seasonal Arctic sea ice forecasting with probabilistic deep learning | doi:; Extended Range Arctic Sea Ice Forecast with Convolutional Long-Short Term Memory Networks | doi:; Advancing global sea ice prediction capabilities using a fully coupled climate model with integrated machine learning | doi:

## 本实例步骤描述
执行“海洋状态和强迫资料时空对齐与样本构造”，统一历史海冰浓度、海气变量和季节信息的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 本实例执行 prompt
依据{OCEAN_GRID}、{COAST_MASK_POLICY}、{PREPROCESS_CONFIG}完成海洋状态和强迫资料时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 本实例输入槽
- {OCEAN_GRID} | required=True | type=str | var_name=海洋网格 | hint=输入水平垂向网格规格。 | default=None
- {COAST_MASK_POLICY} | required=True | type=str | var_name=岸线掩膜规则 | hint=输入岸线掩膜规则。 | default=None
- {PREPROCESS_CONFIG} | required=True | type=str | var_name=预处理配置 | hint=输入预处理配置。 | default=None

## 本实例产出
- 对齐后的标准输入
- 掩膜与样本索引
- 预处理转换记录

## 本实例质量门禁
- 预处理后的时间轴、坐标、单位和形状可检查
- 每项插值、归一化、掩膜和缺测处理均有记录
- 不存在由验证资料或未来资料造成的信息泄漏
- 强迫与状态资料的有效时间满足任务边界

## 可调资源（edge:resource，仅真实存在）
- datasets/CMEMS
- datasets/glorys12-global-ocean-reanalysis-dataset
- models/matern-gaussian-process-regression
- tools/glo12v4-operational-ocean-forecasting-system
- tools/multi-task-deep-learning-model-for-indian-ocean-dipole-prediction
- tools/wenhai-global-ocean-forecast-system

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
