# 实例任务：天气暴露和目标观测时空对齐与样本构造 @ E58

- domain: climate
- 骨架: tk-climate-ebe69297
- 场景: sc-66c922e3 (E58)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- E58
- 关联论文: Forecasting Corn Yield With Machine Learning Ensembles | doi:; Maize yield forecasting by linear regression and artificial neural networks in Jilin, China | doi:

## 本实例步骤描述
执行“天气暴露和目标观测时空对齐与样本构造”，统一截至签发日天气、土壤、种植管理和历史产量的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 本实例执行 prompt
依据{ALIGNMENT_CONFIG}、{TREND_FEATURE_POLICY}、{FORWARD_SPLIT_PROTOCOL}完成天气暴露和目标观测时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 本实例输入槽
- {ALIGNMENT_CONFIG} | required=True | type=str | var_name=县域时空对齐 | hint=输入县域时空对齐配置。 | default=None
- {TREND_FEATURE_POLICY} | required=True | type=str | var_name=产量趋势规则 | hint=输入产量趋势处理规则。 | default=None
- {FORWARD_SPLIT_PROTOCOL} | required=True | type=str | var_name=前推验证协议 | hint=输入按年份前推协议。 | default=None

## 本实例产出
- 对齐后的标准输入
- 掩膜与样本索引
- 预处理转换记录

## 本实例质量门禁
- 预处理后的时间轴、坐标、单位和形状可检查
- 每项插值、归一化、掩膜和缺测处理均有记录
- 不存在由验证资料或未来资料造成的信息泄漏
- 训练验证划分阻断同一地点或事件的信息泄漏

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
