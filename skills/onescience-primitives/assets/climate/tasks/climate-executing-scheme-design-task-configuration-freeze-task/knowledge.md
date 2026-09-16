# 骨架任务：执行方案设计与任务配置冻结

- domain: climate
- 复用场景数: 9
- 实例任务数: 9

## 步骤描述（跨场景聚合去重）
- 由agent根据预检结果形成方法、数据、资源、验证和失败分支方案，冻结任务范围、运行配置与验收口径。

## 执行 prompt（跨场景聚合去重）
- {CORRECTION_SCOPE}均为可选输入：未提供的规则或方案字段由agent依据s01预检结果形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。围绕{CORRECTION_SCOPE}、{GPU_ENVIRONMENT}和{RESOURCE_BUDGET}形成订正方法、极端样本保护、基线、试运行和部署方案，并定义s03最小干运行范围后冻结任务配置。将任务范围、数据契约、方法、资源、运行环境和验收协议写入版本化任务配置；关键字段无法冻结时标记BLOCKED，配置冻结后方可进入s03。
- {CORRECTION_SCOPE}均为可选输入：未提供的规则或方案字段由agent依据s01预检结果形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。围绕{CORRECTION_SCOPE}、{GPU_ENVIRONMENT}和{RESOURCE_BUDGET}提交偏差订正方法、基线、分层验证和部署方案，并定义s03最小干运行范围；改善指标未由s02冻结前不得宣称目标已满足。将任务范围、数据契约、方法、资源、运行环境和验收协议写入版本化任务配置；关键字段无法冻结时标记BLOCKED，配置冻结后方可进入s03。
- {INUNDATION_PRODUCT_SPEC}均为可选输入：未提供的规则或方案字段由agent依据s01预检结果形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。围绕{INUNDATION_PRODUCT_SPEC}、{GPU_ENVIRONMENT}和{RESOURCE_BUDGET}提交漫滩快速模拟、产品制作、独立验证和计时方案，并定义s03小范围干运行。将任务范围、数据契约、方法、资源、运行环境和验收协议写入版本化任务配置；关键字段无法冻结时标记BLOCKED，配置冻结后方可进入s03。
- {PHYSICAL_CONSTRAINT_SPEC}均为可选输入：未提供的规则或方案字段由agent依据s01预检结果形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。围绕{PHYSICAL_CONSTRAINT_SPEC}、{GPU_ENVIRONMENT}和{RESOURCE_BUDGET}提交联合温盐流方案，明确海水状态方程等约束如何嵌入神经网络并验证，定义s03最小干运行范围，并冻结1/36°含义和指标口径。将任务范围、数据契约、方法、资源、运行环境和验收协议写入版本化任务配置；关键字段无法冻结时标记BLOCKED，配置冻结后方可进入s03。
- {REALTIME_SERVICE_SPEC}均为可选输入：未提供的规则或方案字段由agent依据s01预检结果形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。围绕{REALTIME_SERVICE_SPEC}、{GPU_ENVIRONMENT}和{RESOURCE_BUDGET}提交实时接入、更新预报、缺测降级、验证和部署方案，并定义s03最小干运行范围与计时口径。将任务范围、数据契约、方法、资源、运行环境和验收协议写入版本化任务配置；关键字段无法冻结时标记BLOCKED，配置冻结后方可进入s03。
- {REFINEMENT_AREAS}均为可选输入：未提供的规则或方案字段由agent依据s01预检结果形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。结合{REFINEMENT_AREAS}、{GPU_ENVIRONMENT}和{RESOURCE_BUDGET}形成海浪预报、浅水与边界约束、二维谱、验证和部署方案，并定义s03最小干运行范围后冻结任务配置。将任务范围、数据契约、方法、资源、运行环境和验收协议写入版本化任务配置；关键字段无法冻结时标记BLOCKED，配置冻结后方可进入s03。
- {TRANSFER_TRAINING_SCOPE}均为可选输入：未提供的规则或方案字段由agent依据s01预检结果形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。围绕{TRANSFER_TRAINING_SCOPE}、{GPU_ENVIRONMENT}和{RESOURCE_BUDGET}形成区域化迁移、边界约束、验证和部署方案，并定义s03最小干运行范围；变量和验收口径未冻结前不得进入s03。将任务范围、数据契约、方法、资源、运行环境和验收协议写入版本化任务配置；关键字段无法冻结时标记BLOCKED，配置冻结后方可进入s03。
- 围绕{DOWNSCALING_PRODUCT_SPEC}、{GPU_ENVIRONMENT}和{RESOURCE_BUDGET}提交订正、降尺度、细节验证、部署和失败分支方案，定义s03最小干运行范围并冻结30%改善口径。将任务范围、数据契约、方法、资源、运行环境和验收协议写入版本化任务配置；关键字段无法冻结时标记BLOCKED，配置冻结后方可进入s03。
- 围绕{OPERATIONAL_SCHEDULE}、{GPU_ENVIRONMENT}和{RESOURCE_BUDGET}形成订正方法、极端事件评估、部署和失败分支方案，定义s03最小干运行范围并冻结指标口径。将任务范围、数据契约、方法、资源、运行环境和验收协议写入版本化任务配置；关键字段无法冻结时标记BLOCKED，配置冻结后方可进入s03。

## 输入槽（var/hint/default）
- {DOWNSCALING_PRODUCT_SPEC} | required=True | type=str | var_name=降尺度产品规格 | hint=输入1km三维产品定义。 | default=水平分辨率1km
- {GPU_ENVIRONMENT} | required=True | type=str | var_name=目标GPU环境 | hint=输入GPU环境与调度信息。 | default=None
- {RESOURCE_BUDGET} | required=True | type=str | var_name=资源与时间预算 | hint=输入可用资源和期限。 | default=None
- {PHYSICAL_CONSTRAINT_SPEC} | required=False | type=str | var_name=物理约束规格 | hint=输入状态方程等约束。 | default=None
- {REALTIME_SERVICE_SPEC} | required=False | type=str | var_name=实时服务规格 | hint=输入触发与失败降级规则。 | default=None
- {OPERATIONAL_SCHEDULE} | required=True | type=str | var_name=业务运行频次 | hint=输入每日运行时刻。 | default=每日两次
- {TRANSFER_TRAINING_SCOPE} | required=False | type=str | var_name=迁移训练范围 | hint=输入可训练层与目标范围。 | default=None
- {CORRECTION_SCOPE} | required=False | type=str | var_name=订正范围 | hint=输入变量区域时效范围。 | default=None
- {REFINEMENT_AREAS} | required=False | type=str | var_name=重点加密区域 | hint=输入岸线浴场渔场清单。 | default=None
- {INUNDATION_PRODUCT_SPEC} | required=False | type=str | var_name=淹没产品规格 | hint=输入分辨率变量和格式。 | default=None

## 产出
- 冻结的执行与验收方案
- 版本化任务配置
- 资源估算、风险和失败分支

## 质量门禁 quality_gate
- 任务范围、配置口径和高成本工作边界已经由agent冻结并留存版本记录
- 必需数据、可选数据、获取责任和缺失时的阻断条件已列明
- 指标公式、基线、验证资料、样本范围和计时边界已列明
- 方案说明方法、数据和资源选择理由且未把实现细节冒充既定任务条件

## 可调资源（edge:resource，仅真实存在）
- datasets/modis-myd13a3-ndvi-product
- datasets/sgp-c1-multi-source-boundary-layer-height-dataset
- datasets/snodas-swe-data-product
- models/anomaly-numerical-correction-with-observations-ano
- models/customized-deep-learning-for-precipitation-bias-correction-and-downscaling
- models/dynamic-pre-training-for-time-series-dynpt
- models/glm-downscaling-methods
- models/narx-network-configurations-for-inundation-depth-forecasting
- models/neural-network-soil-moisture-downscaling
- tools/cnn1-and-cnn10-models-for-downscaling
- tools/glo12v4-operational-ocean-forecasting-system
- tools/urban-hydrological-hydraulic-model-chain-for-inundation-simulation

## 实例任务（本骨架在各场景的实例化）
- climate-executing-scheme-design-task-bohai-yellow-sea-fourcastnet-inst
- climate-executing-scheme-design-task-bohai-yellow-sea-wave-inst
- climate-executing-scheme-design-task-bohai-yellow-sea-wave-inst-2
- climate-executing-scheme-design-task-bohai-yellow-sea-wrf-numeric-inst
- climate-executing-scheme-design-task-nearshore-inundation-rapid-inst
- climate-executing-scheme-design-task-north-sea-3d-sea-temperature-inst
- climate-executing-scheme-design-task-north-sea-3d-temperature-inst
- climate-executing-scheme-design-task-north-sea-storm-surge-inst
- climate-executing-scheme-design-task-north-sea-storm-surge-inst-2

## 复用场景
- E103
- E104
- E101
- E102
- E107
- E108
- E105
- E106
- E109
