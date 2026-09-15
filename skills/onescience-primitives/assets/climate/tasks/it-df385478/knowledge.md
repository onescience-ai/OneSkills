# 实例任务：污染气象资料时空对齐与样本构造 @ E60

- domain: climate
- 骨架: tk-climate-55edfa14
- 场景: sc-f4bb308a (E60)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- E60
- 关联论文: Spatiotemporal deep learning model for citywide air pollution interpolation and prediction | doi:; PM10 and PM2.5 real-time prediction models using an interpolated convolutional neural network | doi:

## 本实例步骤描述
执行“污染气象资料时空对齐与样本构造”，统一稀疏污染站序列、气象、道路和空间位置的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 本实例执行 prompt
依据{ALIGNMENT_CONFIG}、{QUALITY_MASK}、{MISSING_VALUE_POLICY}完成污染气象资料时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 本实例输入槽
- {ALIGNMENT_CONFIG} | required=True | type=str | var_name=时空对齐配置 | hint=输入时空对齐配置。 | default=None
- {QUALITY_MASK} | required=False | type=str | var_name=质量掩膜 | hint=输入质量掩膜路径。 | default=None
- {MISSING_VALUE_POLICY} | required=True | type=str | var_name=缺测处理规则 | hint=输入缺测处理规则。 | default=None

## 本实例产出
- 对齐后的标准输入
- 掩膜与样本索引
- 预处理转换记录

## 本实例质量门禁
- 预处理后的时间轴、坐标、单位和形状可检查
- 每项插值、归一化、掩膜和缺测处理均有记录
- 不存在由验证资料或未来资料造成的信息泄漏
- 站点、网格、单位和质量标志已统一

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
