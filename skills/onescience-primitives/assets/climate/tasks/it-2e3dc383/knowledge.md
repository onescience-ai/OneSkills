# 实例任务：情景外强迫时空对齐与样本构造 @ E57

- domain: climate
- 骨架: tk-climate-6d145e91
- 场景: sc-f46bfa08 (E57)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- E57
- 关联论文: ACE_ A fast, skillful learned global atmospheric model for climate prediction | doi:; Neural general circulation models for weather and climate | doi:

## 本实例步骤描述
执行“情景外强迫时空对齐与样本构造”，统一海温、太阳辐射、地形及初始大气状态的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 本实例执行 prompt
依据{CALENDAR_AND_GRID}、{PREPROCESS_CONFIG}、{SPLIT_PROTOCOL}完成情景外强迫时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 本实例输入槽
- {CALENDAR_AND_GRID} | required=True | type=str | var_name=日历与网格 | hint=输入日历和网格规格。 | default=None
- {PREPROCESS_CONFIG} | required=True | type=str | var_name=预处理配置 | hint=输入预处理配置。 | default=None
- {SPLIT_PROTOCOL} | required=True | type=str | var_name=回报划分协议 | hint=输入按年份划分协议。 | default=None

## 本实例产出
- 对齐后的标准输入
- 掩膜与样本索引
- 预处理转换记录

## 本实例质量门禁
- 预处理后的时间轴、坐标、单位和形状可检查
- 每项插值、归一化、掩膜和缺测处理均有记录
- 不存在由验证资料或未来资料造成的信息泄漏
- 回报或验证年份未参与参数选择

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
