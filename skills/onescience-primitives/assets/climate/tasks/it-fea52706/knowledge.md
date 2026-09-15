# 实例任务：遥感观测标签时空对齐与样本构造 @ E54

- domain: climate
- 骨架: tk-climate-71af4802
- 场景: sc-c918ffdf (E54)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- E54
- 关联论文: Characterisation of the artificial neural network CiPS for cirrus cloud remote sensing with MSG-SEVIRI | doi:; Cirrus cloud retrieval with MSG-SEVIRI using artificial neural networks | doi:

## 本实例步骤描述
执行“遥感观测标签时空对齐与样本构造”，统一静止卫星多光谱辐亮度、观测几何和辅助大气场的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 本实例执行 prompt
依据{CALIBRATION_CONFIG}、{COREGISTRATION_CONFIG}、{TILE_CONFIG}完成遥感观测标签时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 本实例输入槽
- {CALIBRATION_CONFIG} | required=True | type=str | var_name=辐射定标配置 | hint=输入定标配置。 | default=None
- {COREGISTRATION_CONFIG} | required=True | type=str | var_name=几何配准配置 | hint=输入几何配准配置。 | default=None
- {TILE_CONFIG} | required=True | type=str | var_name=切片配置 | hint=输入切片和重叠配置。 | default=None

## 本实例产出
- 对齐后的标准输入
- 掩膜与样本索引
- 预处理转换记录

## 本实例质量门禁
- 预处理后的时间轴、坐标、单位和形状可检查
- 每项插值、归一化、掩膜和缺测处理均有记录
- 不存在由验证资料或未来资料造成的信息泄漏
- 辐射定标、几何配准和质量掩膜均有记录

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
