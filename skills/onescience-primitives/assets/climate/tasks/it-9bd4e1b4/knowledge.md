# 实例任务：致灾因子和事件标签时空对齐与样本构造 @ E76

- domain: climate
- 骨架: tk-climate-f091d868
- 场景: sc-535f1fa2 (E76)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- E76
- 关联论文: Investigating the Role of the Key Conditioning Factors in Flood Susceptibility Mapping Through Machine Learning Approaches | doi:

## 本实例步骤描述
执行“致灾因子和事件标签时空对齐与样本构造”，统一DEM、河网、土地覆盖、土壤、历史洪水样点的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 本实例执行 prompt
依据{STATIC_FEATURE_CONFIG}、{SPATIAL_SPLIT_PROTOCOL}、{IMBALANCE_POLICY}完成致灾因子和事件标签时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 本实例输入槽
- {STATIC_FEATURE_CONFIG} | required=True | type=str | var_name=静态因子配置 | hint=输入静态因子派生配置。 | default=None
- {SPATIAL_SPLIT_PROTOCOL} | required=True | type=str | var_name=空间分块协议 | hint=输入空间分块验证协议。 | default=None
- {IMBALANCE_POLICY} | required=True | type=str | var_name=样本不平衡规则 | hint=输入不平衡处理规则。 | default=None

## 本实例产出
- 对齐后的标准输入
- 掩膜与样本索引
- 预处理转换记录

## 本实例质量门禁
- 预处理后的时间轴、坐标、单位和形状可检查
- 每项插值、归一化、掩膜和缺测处理均有记录
- 不存在由验证资料或未来资料造成的信息泄漏
- 正负样本构造保留真实发生率并记录抽样策略

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
