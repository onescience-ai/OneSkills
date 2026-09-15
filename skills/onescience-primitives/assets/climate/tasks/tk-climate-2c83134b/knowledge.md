# 骨架任务：数据对齐、样本构建与最小干运行

- domain: climate
- 复用场景数: 8
- 实例任务数: 8

## 步骤描述（跨场景聚合去重）
- 按冻结方案完成时间、空间、变量、单位和质量标志对齐，建立开发与独立验证样本，并在目标环境完成最小干运行。

## 执行 prompt（跨场景聚合去重）
- 仅在s02任务配置冻结门禁通过后执行。{BOUNDARY_ALIGNMENT_SPEC}、{DATA_ALIGNMENT_SPEC}、{SAMPLE_SPLIT_SPEC}均为可选输入：未提供的规则或方案字段由agent依据s02冻结方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。按{VARIABLES_AND_LEVELS}、{BOUNDARY_ALIGNMENT_SPEC}、{DATA_ALIGNMENT_SPEC}和{SAMPLE_SPLIT_SPEC}对齐全球模型输入、区域再分析与边界产品，建立无时间泄漏的训练、调参与独立验证样本并保留处理记录。完成对齐与样本构建后，运行s02冻结的最小案例，实际验证数据读取、核心计算或模型构建与加载、单批次前向或短流程以及结果写出，并保存输入快照、配置和日志；最小干运行不得作为精度或业务性能通过证据。
- 仅在s02任务配置冻结门禁通过后执行。{FORECAST_TRUTH_MATCHING}、{DATA_ALIGNMENT_SPEC}、{SAMPLE_SPLIT_SPEC}均为可选输入：未提供的规则或方案字段由agent依据s02冻结方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。按{TARGET_GRID}、{FORECAST_TRUTH_MATCHING}、{DATA_ALIGNMENT_SPEC}和{SAMPLE_SPLIT_SPEC}建立当天预报、前日模拟、气象场与观测配对，单独标记>100 cm事件并保持独立验证。完成对齐与样本构建后，运行s02冻结的最小案例，实际验证数据读取、核心计算或模型构建与加载、单批次前向或短流程以及结果写出，并保存输入快照、配置和日志；最小干运行不得作为精度或业务性能通过证据。
- 仅在s02任务配置冻结门禁通过后执行。{FORECAST_TRUTH_MATCHING}、{DATA_ALIGNMENT_SPEC}、{SAMPLE_SPLIT_SPEC}均为可选输入：未提供的规则或方案字段由agent依据s02冻结方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。按{VARIABLES_AND_LEVELS}、{FORECAST_TRUTH_MATCHING}、{DATA_ALIGNMENT_SPEC}和{SAMPLE_SPLIT_SPEC}构建WRF预报—WRF-ERA5配对样本，记录插值和质量处理，防止相邻起报或年份泄漏。完成对齐与样本构建后，运行s02冻结的最小案例，实际验证数据读取、核心计算或模型构建与加载、单批次前向或短流程以及结果写出，并保存输入快照、配置和日志；最小干运行不得作为精度或业务性能通过证据。
- 仅在s02任务配置冻结门禁通过后执行。{HIGH_RES_TEMPERATURE_REFERENCE}、{VERTICAL_COORDINATE_SPEC}、{DATA_ALIGNMENT_SPEC}、{SAMPLE_SPLIT_SPEC}均为可选输入：未提供的规则或方案字段由agent依据s02冻结方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。按{HIGH_RES_TEMPERATURE_REFERENCE}、{VERTICAL_COORDINATE_SPEC}、{DATA_ALIGNMENT_SPEC}和{SAMPLE_SPLIT_SPEC}对齐三维海温、SST观测、气象强迫和高分辨率参考，建立无泄漏样本。完成对齐与样本构建后，运行s02冻结的最小案例，实际验证数据读取、核心计算或模型构建与加载、单批次前向或短流程以及结果写出，并保存输入快照、配置和日志；最小干运行不得作为精度或业务性能通过证据。
- 仅在s02任务配置冻结门禁通过后执行。{OCEAN_REFERENCE_DATA}、{DATA_ALIGNMENT_SPEC}、{SAMPLE_SPLIT_SPEC}均为可选输入：未提供的规则或方案字段由agent依据s02冻结方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。按{OCEAN_REFERENCE_DATA}、{VERTICAL_COORDINATE_SPEC}、{DATA_ALIGNMENT_SPEC}和{SAMPLE_SPLIT_SPEC}对齐初始场、强迫、边界、地形与参考，建立无泄漏的三维训练和独立验证样本。完成对齐与样本构建后，运行s02冻结的最小案例，实际验证数据读取、核心计算或模型构建与加载、单批次前向或短流程以及结果写出，并保存输入快照、配置和日志；最小干运行不得作为精度或业务性能通过证据。
- 仅在s02任务配置冻结门禁通过后执行。{REALTIME_ALIGNMENT_SPEC}、{DATA_ALIGNMENT_SPEC}、{SAMPLE_SPLIT_SPEC}均为可选输入：未提供的规则或方案字段由agent依据s02冻结方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。按{REALTIME_ALIGNMENT_SPEC}、{TARGET_GRID}、{DATA_ALIGNMENT_SPEC}和{SAMPLE_SPLIT_SPEC}构建历史实时回放和独立验证样本，确保每次回放只使用当时可获得资料。完成对齐与样本构建后，运行s02冻结的最小案例，实际验证数据读取、核心计算或模型构建与加载、单批次前向或短流程以及结果写出，并保存输入快照、配置和日志；最小干运行不得作为精度或业务性能通过证据。
- 仅在s02任务配置冻结门禁通过后执行。{WAVE_VARIABLE_CONTRACT}、{DATA_ALIGNMENT_SPEC}、{SAMPLE_SPLIT_SPEC}均为可选输入：未提供的规则或方案字段由agent依据s02冻结方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。按{WAVE_REFERENCE_DATA}、{WAVE_VARIABLE_CONTRACT}、{DATA_ALIGNMENT_SPEC}和{SAMPLE_SPLIT_SPEC}对齐地形、岸线、风场、边界和海浪参考，建立无未来泄漏的训练与独立验证样本。完成对齐与样本构建后，运行s02冻结的最小案例，实际验证数据读取、核心计算或模型构建与加载、单批次前向或短流程以及结果写出，并保存输入快照、配置和日志；最小干运行不得作为精度或业务性能通过证据。
- 仅在s02任务配置冻结门禁通过后执行。{WAVE_VARIABLE_CONTRACT}、{FORECAST_TRUTH_MATCHING}、{DATA_ALIGNMENT_SPEC}、{SAMPLE_SPLIT_SPEC}均为可选输入：未提供的规则或方案字段由agent依据s02冻结方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。按{WAVE_VARIABLE_CONTRACT}、{FORECAST_TRUTH_MATCHING}、{DATA_ALIGNMENT_SPEC}和{SAMPLE_SPLIT_SPEC}建立原始预报—观测配对，保持原模式契约并防止相邻时次和事件泄漏。完成对齐与样本构建后，运行s02冻结的最小案例，实际验证数据读取、核心计算或模型构建与加载、单批次前向或短流程以及结果写出，并保存输入快照、配置和日志；最小干运行不得作为精度或业务性能通过证据。

## 输入槽（var/hint/default）
- {HIGH_RES_TEMPERATURE_REFERENCE} | required=False | type=str | var_name=高分辨率海温参考 | hint=输入独立海温参考路径。 | default=None
- {VERTICAL_COORDINATE_SPEC} | required=True | type=str | var_name=垂向坐标规格 | hint=输入层次深度定义。 | default=垂向不少于30层
- {DATA_ALIGNMENT_SPEC} | required=False | type=str | var_name=数据对齐规格 | hint=可输入已冻结对齐规则。 | default=None
- {SAMPLE_SPLIT_SPEC} | required=False | type=str | var_name=样本划分规格 | hint=可输入已冻结划分规则。 | default=None
- {OCEAN_REFERENCE_DATA} | required=False | type=str | var_name=温盐流参考资料 | hint=输入训练验证参考路径。 | default=None
- {REALTIME_ALIGNMENT_SPEC} | required=False | type=str | var_name=实时资料对齐规则 | hint=输入延迟缺测对齐规则。 | default=None
- {TARGET_GRID} | required=True | type=str | var_name=目标网格 | hint=输入北海区近岸网格。 | default=近岸300m
- {FORECAST_TRUTH_MATCHING} | required=False | type=str | var_name=预报观测配对规则 | hint=输入起报有效时刻规则。 | default=None
- {VARIABLES_AND_LEVELS} | required=True | type=str | var_name=订正变量与层次 | hint=输入变量和垂直层次。 | default=None
- {BOUNDARY_ALIGNMENT_SPEC} | required=False | type=str | var_name=边界对齐规格 | hint=输入边界时空对齐规则。 | default=None
- {WAVE_VARIABLE_CONTRACT} | required=False | type=str | var_name=海浪变量契约 | hint=输入变量单位方向约定。 | default=None
- {WAVE_REFERENCE_DATA} | required=True | type=str | var_name=海浪参考资料 | hint=输入观测或参考场路径。 | default=None

## 产出
- 对齐后的模型数据集
- 开发—调参—独立验证样本索引
- 数据质量、处理记录和最小干运行日志

## 质量门禁 quality_gate
- 方法构建或配置、参数选择和独立验证资料用途隔离且无时间或空间泄漏
- 时间、空间、变量、单位和坐标语义一致
- 最小干运行满足输入输出契约并无异常数值
- 本步骤声明的全部必要外部数据、基础模型工件（如适用）和软件依赖均已实际获得、可读且版本冻结；只有获取方案而尚未取得本步骤必要输入时，本步骤不得通过
- 模型、依赖、GPU环境和数据接口兼容
- 缺测、异常、插补和剔除均有记录，处理前后数据可追溯

## 可调资源（edge:resource，仅真实存在）
- datasets/ERA5

## 实例任务（本骨架在各场景的实例化）
- it-04d5302d
- it-0a04a9d3
- it-17e4703d
- it-29dd078b
- it-507fa709
- it-8e87c16d
- it-90495916
- it-f7fb2778

## 复用场景
- E103
- E104
- E101
- E102
- E107
- E108
- E105
- E106
