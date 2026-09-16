# 骨架任务：预报实况样本时空对齐与样本构造

- domain: climate
- 复用场景数: 2
- 实例任务数: 2

## 步骤描述（跨场景聚合去重）
- 执行“预报实况样本时空对齐与样本构造”，统一原始集合成员、辅助预报量、站点历史观测的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- 执行“预报实况样本时空对齐与样本构造”，统一集合NWP辐射、历史观测与误差的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 执行 prompt（跨场景聚合去重）
- 依据{MATCHING_CONFIG}、{SPLIT_PROTOCOL}、{MISSING_VALUE_POLICY}完成预报实况样本时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 输入槽（var/hint/default）
- {MATCHING_CONFIG} | required=True | type=str | var_name=预报实况配对 | hint=输入预报实况配对规则。 | default=None
- {SPLIT_PROTOCOL} | required=True | type=str | var_name=数据划分协议 | hint=输入时间划分协议。 | default=None
- {MISSING_VALUE_POLICY} | required=True | type=str | var_name=缺测处理规则 | hint=输入缺测处理规则。 | default=None

## 产出
- 对齐后的标准输入
- 掩膜与样本索引
- 预处理转换记录

## 质量门禁 quality_gate
- 不存在由验证资料或未来资料造成的信息泄漏
- 校准、验证和测试时段互斥且无未来信息泄漏
- 每项插值、归一化、掩膜和缺测处理均有记录
- 预处理后的时间轴、坐标、单位和形状可检查

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 实例任务（本骨架在各场景的实例化）
- climate-forecast-actual-samples-ensemble-forecast-intraday-inst
- climate-forecast-actual-samples-station-temperature-ensemble-inst

## 复用场景
- E14
- E24
