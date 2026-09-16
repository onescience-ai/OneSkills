# 实例任务：源观测和参考资料时空对齐与样本构造 @ E61

- domain: climate
- 骨架: climate-source-obs-reference-stalign-sample-task
- 场景: climate-lidar-sounding-fusion-boundary-layer-height-retrieval-scenario (E61)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- E61
- 关联论文: On the estimation of boundary layer heights- a machine learning approach | doi:; Deriving boundary layer height from aerosol lidar using machine learning- KABL and ADABL algorithms | doi:

## 本实例步骤描述
执行“源观测和参考资料时空对齐与样本构造”，统一激光雷达后向散射剖面、探空、地面气象的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 本实例执行 prompt
依据{ALIGNMENT_CONFIG}、{QUALITY_CONTROL}、{REFERENCE_DEFINITION}完成源观测和参考资料时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 本实例输入槽
- {ALIGNMENT_CONFIG} | required=True | type=str | var_name=时空对齐配置 | hint=输入时空对齐配置。 | default=None
- {QUALITY_CONTROL} | required=True | type=str | var_name=质量控制配置 | hint=输入质量控制配置。 | default=None
- {REFERENCE_DEFINITION} | required=False | type=str | var_name=参考定义 | hint=输入标签或参考定义。 | default=None

## 本实例产出
- 对齐后的标准输入
- 掩膜与样本索引
- 预处理转换记录

## 本实例质量门禁
- 预处理后的时间轴、坐标、单位和形状可检查
- 每项插值、归一化、掩膜和缺测处理均有记录
- 不存在由验证资料或未来资料造成的信息泄漏
- 同期资料在坐标、单位和质量标志上严格对齐

## 可调资源（edge:resource，仅真实存在）
- datasets/south-korea-air-quality-and-weather-monitoring-dataset

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
