# 实例任务：水文强迫和流域资料时空对齐与样本构造 @ E66

- domain: climate
- 骨架: tk-climate-8a3f6bde
- 场景: sc-db022c00 (E66)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- E66
- 关联论文: Hybrid Deep Learning for Week-Ahead Evapotranspiration Forecasting | doi:; Neural network approach to reference evapotranspiration modeling from limited climatic data in arid regions | doi:

## 本实例步骤描述
执行“水文强迫和流域资料时空对齐与样本构造”，统一温度湿度风速辐射观测与预报的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 本实例执行 prompt
依据{TIME_ALIGNMENT_CONFIG}、{REFERENCE_ET_DEFINITION}、{MISSING_VALUE_POLICY}完成水文强迫和流域资料时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 本实例输入槽
- {TIME_ALIGNMENT_CONFIG} | required=True | type=str | var_name=时间对齐配置 | hint=输入预报实况对齐配置。 | default=None
- {REFERENCE_ET_DEFINITION} | required=True | type=str | var_name=参考蒸散发定义 | hint=输入参考蒸散发定义。 | default=None
- {MISSING_VALUE_POLICY} | required=True | type=str | var_name=缺测处理规则 | hint=输入缺测处理规则。 | default=None

## 本实例产出
- 对齐后的标准输入
- 掩膜与样本索引
- 预处理转换记录

## 本实例质量门禁
- 预处理后的时间轴、坐标、单位和形状可检查
- 每项插值、归一化、掩膜和缺测处理均有记录
- 不存在由验证资料或未来资料造成的信息泄漏
- 训练验证按时间或流域隔离并防止未来泄漏

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
