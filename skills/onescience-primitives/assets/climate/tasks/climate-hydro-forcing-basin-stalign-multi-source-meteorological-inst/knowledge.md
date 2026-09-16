# 实例任务：水文强迫和流域资料时空对齐与样本构造 @ E10

- domain: climate
- 骨架: climate-hydro-forcing-basin-stalign-sample-task
- 场景: climate-multi-source-meteorological-forcing-driven-multi-basin-daily-scenario (E10)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- E10
- 关联论文: A note on leveraging synergy in multiple meteorological data sets with deep learning for rainfall–runoff modeling | doi:; Hydrologically informed machine learning for rainfall–runoff modelling: towards distributed modelling | doi:; Rainfall–runoff modelling using Long Short-Term Memory (LSTM) networks | doi:; Rainfall–Runoff Prediction at Multiple Timescales with a Single Long Short-Term Memory Network | doi:

## 本实例步骤描述
执行“水文强迫和流域资料时空对齐与样本构造”，统一多源逐日气象强迫、流域静态属性、历史流量的时间、空间、单位、质量标志和缺测处理，形成可复现输入。

## 本实例执行 prompt
依据{TIME_RESOLUTION}、{SPATIAL_MAPPING}、{WARMUP_POLICY}、{MISSING_VALUE_POLICY}完成水文强迫和流域资料时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。

## 本实例输入槽
- {TIME_RESOLUTION} | required=True | type=str | var_name=时间分辨率 | hint=输入时间分辨率。 | default=None
- {SPATIAL_MAPPING} | required=True | type=str | var_name=空间映射配置 | hint=输入流域空间映射配置。 | default=None
- {WARMUP_POLICY} | required=False | type=str | var_name=预热期规则 | hint=输入状态预热规则。 | default=None
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
- datasets/spatial-generalization-benchmarks-for-hydrologic-models
- models/dynamic-pre-training-for-time-series-dynpt
- models/spatial-and-temporal-deep-learning-models-for-fire-prediction

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
