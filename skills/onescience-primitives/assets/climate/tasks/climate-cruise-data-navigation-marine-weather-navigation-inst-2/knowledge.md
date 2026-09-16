# 实例任务：航次资料和航行约束时空对齐与样本构造 @ E100

- domain: climate
- 骨架: climate-cruise-data-navigation-constraint-alignment-and-sampling-task
- 场景: climate-marine-weather-navigation-constraint-ship-route-optimization-scenario (E100)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- E100
- 关联论文: A novel, data-driven heuristic framework for vessel weather routing | doi:

## 本实例步骤描述
执行“航次资料和航行约束时空对齐与样本构造”，统一风浪流预报、船舶性能、起终点与约束的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 本实例执行 prompt
依据{ROUTING_GRID}、{INTERPOLATION_CONFIG}、{CONSTRAINT_POLICY}完成航次资料和航行约束时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 本实例输入槽
- {ROUTING_GRID} | required=True | type=str | var_name=航行网格 | hint=输入航行网格规格。 | default=None
- {INTERPOLATION_CONFIG} | required=True | type=str | var_name=插值配置 | hint=输入风浪流插值配置。 | default=None
- {CONSTRAINT_POLICY} | required=True | type=str | var_name=约束处理规则 | hint=输入约束处理规则。 | default=None

## 本实例产出
- 对齐后的标准输入
- 掩膜与样本索引
- 预处理转换记录

## 本实例质量门禁
- 预处理后的时间轴、坐标、单位和形状可检查
- 每项插值、归一化、掩膜和缺测处理均有记录
- 不存在由验证资料或未来资料造成的信息泄漏
- 风浪流已插值到航行时空网格且保留质量标志

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
