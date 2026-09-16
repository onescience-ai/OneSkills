# 实例任务：源观测和参考资料时空对齐与样本构造 @ E21

- domain: climate
- 骨架: climate-source-obs-reference-stalign-sample-task
- 场景: climate-radar-satellite-rain-gauge-multimodal-concurrent-quantitative-scenario (E21)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- E21
- 关联论文: A Deep Learning Multimodal Method for Precipitation Estimation | doi:; Ground radar precipitation estimation with deep learning approaches in meteorological private cloud | doi:; RainForest- a random forest algorithm for quantitative precipitation estimation over Switzerland | doi:; Improving near real-time precipitation estimation using a U-Net convolutional neural network and geographical information | doi:

## 本实例步骤描述
执行“源观测和参考资料时空对齐与样本构造”，统一雷达观测、卫星云图、雨量计及地理特征的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 本实例执行 prompt
依据{COREGISTRATION_CONFIG}、{GAUGE_QC}、{FUSION_GRID}完成源观测和参考资料时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 本实例输入槽
- {COREGISTRATION_CONFIG} | required=True | type=str | var_name=多模态配准 | hint=输入多模态配准配置。 | default=None
- {GAUGE_QC} | required=True | type=str | var_name=雨量计质控 | hint=输入雨量计质控配置。 | default=None
- {FUSION_GRID} | required=True | type=str | var_name=融合目标网格 | hint=输入融合目标网格。 | default=None

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
- models/multivariate-data-fusion-vector-wind-prediction

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
