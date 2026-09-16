# 骨架任务：产品质控与运行性能检查

- domain: climate
- 复用场景数: 9
- 实例任务数: 9

## 步骤描述（跨场景聚合去重）
- 检查产品完整性、物理与统计合理性、时空连续性、异常和目标GPU环境下的运行性能。

## 执行 prompt（跨场景聚合去重）
- {PRODUCT_QC_SPEC}、{RUNTIME_PROTOCOL}、{BOUNDARY_QC_SPEC}均为可选输入：未提供的规则或方案字段由agent依据s02冻结方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。依据{PRODUCT_QC_SPEC}和{BOUNDARY_QC_SPEC}检查产品变量、网格、时次、边界连续性和异常，并按{RUNTIME_PROTOCOL}在目标GPU环境测量72小时预报用时。
- {PRODUCT_QC_SPEC}、{RUNTIME_PROTOCOL}、{FINE_SCALE_QC_SPEC}均为可选输入：未提供的规则或方案字段由agent依据s02冻结方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。依据{PRODUCT_QC_SPEC}和{FINE_SCALE_QC_SPEC}检查层次、单位、海陆边界、空间细节、时序连续性和异常，并按{RUNTIME_PROTOCOL}测量目标GPU运行性能。
- {PRODUCT_QC_SPEC}、{RUNTIME_PROTOCOL}、{LATENCY_POLICY}均为可选输入：未提供的规则或方案字段由agent依据s02冻结方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。依据{PRODUCT_QC_SPEC}和{LATENCY_POLICY}检查实时输入新鲜度、缺测、站点与网格产品连续性和异常，并按{RUNTIME_PROTOCOL}测量单次运行时间。
- {PRODUCT_QC_SPEC}、{RUNTIME_PROTOCOL}、{PHYSICAL_QC_SPEC}均为可选输入：未提供的规则或方案字段由agent依据s02冻结方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。依据{PRODUCT_QC_SPEC}和{PHYSICAL_QC_SPEC}检查层次、单位、温盐范围、流场连续性、状态方程一致性和异常，并按{RUNTIME_PROTOCOL}测量目标GPU运行性能。
- {PRODUCT_QC_SPEC}、{RUNTIME_PROTOCOL}、{RAW_CORRECTED_PAIR_SPEC}均为可选输入：未提供的规则或方案字段由agent依据s02冻结方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。依据{PRODUCT_QC_SPEC}和{RAW_CORRECTED_PAIR_SPEC}检查订正前后产品契约、方向变量、极端波况和异常，并按{RUNTIME_PROTOCOL}测量目标环境运行性能。
- {PRODUCT_QC_SPEC}、{RUNTIME_PROTOCOL}、{RAW_CORRECTED_PAIR_SPEC}均为可选输入：未提供的规则或方案字段由agent依据s02冻结方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。依据{PRODUCT_QC_SPEC}和{RAW_CORRECTED_PAIR_SPEC}检查订正前后产品的变量、网格、时次、单位、异常和不合理改动，并按{RUNTIME_PROTOCOL}测量目标GPU环境运行性能。
- {PRODUCT_QC_SPEC}、{RUNTIME_PROTOCOL}、{SPATIAL_TOPOLOGY_SPEC}均为可选输入：未提供的规则或方案字段由agent依据s02冻结方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。依据{PRODUCT_QC_SPEC}和{SPATIAL_TOPOLOGY_SPEC}检查坐标、高程基准、淹没连通性、海陆边界和行政区划叠加，并按{RUNTIME_PROTOCOL}测量完整流程用时。
- {PRODUCT_QC_SPEC}、{RUNTIME_PROTOCOL}、{SPECTRUM_QC_SPEC}均为可选输入：未提供的规则或方案字段由agent依据s02冻结方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。依据{PRODUCT_QC_SPEC}和{SPECTRUM_QC_SPEC}检查参数范围、方向约定、近岸连续性、边界衔接、风浪与涌浪分量和二维谱，并按{RUNTIME_PROTOCOL}测量运行性能。
- {PRODUCT_QC_SPEC}、{RUNTIME_PROTOCOL}均为可选输入：未提供的规则或方案字段由agent依据s02冻结方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。依据{PRODUCT_QC_SPEC}和{EXTREME_EVENT_THRESHOLD}检查站点与网格产品、潮位连续性、极端过程保持和异常，并按{RUNTIME_PROTOCOL}测量每日两次业务运行性能。

## 输入槽（var/hint/default）
- {PRODUCT_QC_SPEC} | required=False | type=str | var_name=产品质控规格 | hint=输入产品质控规则。 | default=None
- {RUNTIME_PROTOCOL} | required=False | type=str | var_name=运行计时协议 | hint=输入硬件与计时边界。 | default=None
- {FINE_SCALE_QC_SPEC} | required=False | type=str | var_name=细尺度质控规格 | hint=输入空间细节检查规则。 | default=None
- {PHYSICAL_QC_SPEC} | required=False | type=str | var_name=物理一致性质控 | hint=输入温盐流诊断规则。 | default=None
- {LATENCY_POLICY} | required=False | type=str | var_name=实时资料延迟规则 | hint=输入延迟与过期判定。 | default=None
- {EXTREME_EVENT_THRESHOLD} | required=True | type=str | var_name=重点增水阈值 | hint=输入重点事件阈值。 | default=超过100cm
- {BOUNDARY_QC_SPEC} | required=False | type=str | var_name=边界质控规格 | hint=输入边界连续性规则。 | default=None
- {RAW_CORRECTED_PAIR_SPEC} | required=False | type=str | var_name=订正前后配对规格 | hint=输入结果配对检查规则。 | default=None
- {SPECTRUM_QC_SPEC} | required=False | type=str | var_name=二维谱质控规格 | hint=输入谱轴和能量检查规则。 | default=None
- {SPATIAL_TOPOLOGY_SPEC} | required=False | type=str | var_name=空间拓扑规则 | hint=输入连通和边界检查规则。 | default=None

## 产出
- GPU运行性能报告
- 产品完整性与异常报告
- 物理和统计质控报告

## 质量门禁 quality_gate
- 产品变量、单位、坐标、有效时间和质量标志完整
- 缺测、重复、跳变、越界和不合理值已定位并记录
- 质控失败的产品未进入正式验收样本
- 运行性能使用冻结后的目标硬件、数据规模和计时边界测量

## 可调资源（edge:resource，仅真实存在）
- datasets/modis-myd13a3-ndvi-product
- datasets/sgp-c1-multi-source-boundary-layer-height-dataset
- datasets/snodas-swe-data-product
- datasets/spatial-generalization-benchmarks-for-hydrologic-models
- models/dust-event-forecasting-with-multi-task-deep-learning
- models/dynamic-pre-training-for-time-series-dynpt
- models/importance-sampling-strategy-for-extreme-events
- models/spatial-and-temporal-deep-learning-models-for-fire-prediction
- models/tucker-thresholding-method-for-boundary-layer-height-estimation
- tools/ecmwf-hres

## 实例任务（本骨架在各场景的实例化）
- climate-product-quality-control-bohai-yellow-sea-fourcastnet-inst
- climate-product-quality-control-bohai-yellow-sea-wave-inst
- climate-product-quality-control-bohai-yellow-sea-wave-inst-2
- climate-product-quality-control-bohai-yellow-sea-wrf-numeric-inst
- climate-product-quality-control-nearshore-inundation-rapid-inst
- climate-product-quality-control-north-sea-3d-sea-temperature-inst
- climate-product-quality-control-north-sea-3d-temperature-inst
- climate-product-quality-control-north-sea-storm-surge-inst
- climate-product-quality-control-north-sea-storm-surge-inst-2

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
