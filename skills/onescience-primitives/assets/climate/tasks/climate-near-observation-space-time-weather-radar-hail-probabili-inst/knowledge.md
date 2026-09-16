# 实例任务：临近观测时空对齐与样本构造 @ E83

- domain: climate
- 骨架: climate-near-observation-space-time-alignment-sample-construction-task
- 场景: climate-weather-radar-hail-probability-nowcast-0-2h-scenario (E83)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- E83
- 关联论文: A Spatial-temporal Deep Probabilistic Diffusion Model for Reliable Hail Nowcasting with Radar Echo Extrapolation | doi:

## 本实例步骤描述
执行“临近观测时空对齐与样本构造”，统一雷达回波序列、可选环境场、冰雹标签的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 本实例执行 prompt
依据{FRAME_INTERVAL}、{TARGET_GRID}、{QUALITY_CONTROL}、{MISSING_VALUE_POLICY}完成临近观测时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 本实例输入槽
- {FRAME_INTERVAL} | required=True | type=str | var_name=观测帧间隔 | hint=输入观测帧间隔。 | default=None
- {TARGET_GRID} | required=True | type=str | var_name=目标网格 | hint=输入目标网格规格。 | default=None
- {QUALITY_CONTROL} | required=True | type=str | var_name=质量控制配置 | hint=输入质量控制配置。 | default=None
- {MISSING_VALUE_POLICY} | required=True | type=str | var_name=缺帧处理规则 | hint=输入缺帧处理规则。 | default=None

## 本实例产出
- 对齐后的标准输入
- 掩膜与样本索引
- 预处理转换记录

## 本实例质量门禁
- 预处理后的时间轴、坐标、单位和形状可检查
- 每项插值、归一化、掩膜和缺测处理均有记录
- 不存在由验证资料或未来资料造成的信息泄漏
- 缺帧、异常回波和多源延迟已显式记录

## 可调资源（edge:resource，仅真实存在）
- datasets/south-korea-air-quality-and-weather-monitoring-dataset

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
