# 实例任务：源观测和参考资料时空对齐与样本构造 @ E34

- domain: climate
- 骨架: tk-climate-558ec5a0
- 场景: sc-2a31eae0 (E34)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- E34
- 关联论文: A Deep Learning Approach to Radar‐Based QPE | doi:; Integration of shapley additive explanations with random forest model for quantitative precipitation estimation of mesoscale convective systems | doi:; RainForest- a random forest algorithm for quantitative precipitation estimation over Switzerland | doi:

## 本实例步骤描述
执行“源观测和参考资料时空对齐与样本构造”，统一雷达多仰角反射率、雨量计观测、质量标识的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 本实例执行 prompt
依据{RADAR_QC}、{VERTICAL_FEATURE_CONFIG}、{TARGET_GRID}完成源观测和参考资料时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 本实例输入槽
- {RADAR_QC} | required=True | type=str | var_name=雷达质控配置 | hint=输入雷达质控配置。 | default=None
- {VERTICAL_FEATURE_CONFIG} | required=True | type=str | var_name=垂直特征配置 | hint=输入体扫特征配置。 | default=None
- {TARGET_GRID} | required=True | type=str | var_name=雷达目标网格 | hint=输入雷达目标网格。 | default=None

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
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
