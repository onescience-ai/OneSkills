# 实例任务：目标序列及缺口时空对齐与样本构造 @ E13

- domain: climate
- 骨架: climate-target-sequence-gap-alignment-and-sample-construction-task
- 场景: climate-global-ocean-pco2-sparse-observation-spatiotemporal-expansion-scenario (E13)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- E13
- 关联论文: A comparative assessment of the uncertainties of global surface ocean CO 2 estimates using a machine-learning ensemble (CSIR-ML6 version 2019a) – have we hit the wall? | doi:; Global high-resolution monthly p CO 2 climatology for the coastal ocean derived from neural network interpolation | doi:; Spatiotemporal upscaling of sparse air-sea pCO2 data via physics-informed transfer learning | doi:

## 本实例步骤描述
执行“目标序列及缺口时空对齐与样本构造”，统一稀疏海气pCO2观测、海温、盐度和生物地球化学辅助场的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 本实例执行 prompt
依据{ALIGNMENT_CONFIG}、{QUALITY_CONTROL}、{HOLDOUT_MASK_POLICY}完成目标序列及缺口时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 本实例输入槽
- {ALIGNMENT_CONFIG} | required=True | type=str | var_name=时空对齐配置 | hint=输入时空对齐配置。 | default=None
- {QUALITY_CONTROL} | required=True | type=str | var_name=质量控制配置 | hint=输入质量控制配置。 | default=None
- {HOLDOUT_MASK_POLICY} | required=True | type=str | var_name=伪缺口划分规则 | hint=输入伪缺口划分规则。 | default=None

## 本实例产出
- 对齐后的标准输入
- 掩膜与样本索引
- 预处理转换记录

## 本实例质量门禁
- 预处理后的时间轴、坐标、单位和形状可检查
- 每项插值、归一化、掩膜和缺测处理均有记录
- 不存在由验证资料或未来资料造成的信息泄漏
- 伪缺口与独立验证块未参与重建参数选择

## 可调资源（edge:resource，仅真实存在）
- datasets/south-korea-air-quality-and-weather-monitoring-dataset

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
