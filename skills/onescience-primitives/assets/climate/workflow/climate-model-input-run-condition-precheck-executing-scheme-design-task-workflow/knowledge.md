# 工作流：climate-model-input-run-condition-precheck-executing-scheme-design-task-workflow

- domain: climate
- 步骤数: 6
- 共用场景数: 1

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 模型输入与运行条件预检
- desc: 核对模型实际输入的数据身份、版本、权限、资料截止时间、变量、时空覆盖和缺测，形成输入清单与数据阻断项。
- depend: []
- prompt: 读取{OCEAN_TEMPERATURE_FORECAST}、{FUSED_SST_OBSERVATION}和{ATMOSPHERIC_FORCING_FORECAST}，以{TARGET_REGION}和{DATA_CUTOFF_TIME}核验系统版本、起报、有效时刻、层次、网格、缺测和未来资料泄漏。
- step_input:
  - {OCEAN_TEMPERATURE_FORECAST} (required=True, type=str, var_name=海温数值预报, hint=输入三维海温预报路径。, default=None)
  - {FUSED_SST_OBSERVATION} (required=True, type=str, var_name=融合海表温度观测, hint=输入融合SST观测路径。, default=None)
  - {ATMOSPHERIC_FORCING_FORECAST} (required=True, type=str, var_name=气象强迫预报, hint=输入气温降水风场路径。, default=None)
  - {TARGET_REGION} (required=True, type=str, var_name=目标区域, hint=输入北海区区域边界。, default=北海区)
  - {DATA_CUTOFF_TIME} (required=True, type=str, var_name=资料截止时间, hint=输入资料截止时间。, default=None)
- outputs: ['输入数据与版本清单', '输入时空变量与缺测检查报告', '数据缺失、权限和契约阻断项']
- quality_gate: ['输入文件存在、可读、获准使用且来源和版本可追溯', '输入的区域、时段、网格、变量、单位、坐标和资料截止时间已逐项核对', '未来资料、模型开发资料和独立验证资料的用途已隔离', '输入数据中的缺失、冲突和异常未被推测值覆盖']

### s02 执行方案设计与任务配置冻结
- desc: 由agent根据预检结果形成方法、数据、资源、验证和失败分支方案，冻结任务范围、运行配置与验收口径。
- depend: ['s01']
- prompt: 围绕{DOWNSCALING_PRODUCT_SPEC}、{GPU_ENVIRONMENT}和{RESOURCE_BUDGET}提交订正、降尺度、细节验证、部署和失败分支方案，定义s03最小干运行范围并冻结30%改善口径。将任务范围、数据契约、方法、资源、运行环境和验收协议写入版本化任务配置；关键字段无法冻结时标记BLOCKED，配置冻结后方可进入s03。
- step_input:
  - {DOWNSCALING_PRODUCT_SPEC} (required=True, type=str, var_name=降尺度产品规格, hint=输入1km三维产品定义。, default=水平分辨率1km)
  - {GPU_ENVIRONMENT} (required=True, type=str, var_name=目标GPU环境, hint=输入GPU环境与调度信息。, default=None)
  - {RESOURCE_BUDGET} (required=True, type=str, var_name=资源与时间预算, hint=输入可用资源和期限。, default=None)
- outputs: ['冻结的执行与验收方案', '版本化任务配置', '资源估算、风险和失败分支']
- quality_gate: ['方案说明方法、数据和资源选择理由且未把实现细节冒充既定任务条件', '必需数据、可选数据、获取责任和缺失时的阻断条件已列明', '指标公式、基线、验证资料、样本范围和计时边界已列明', '任务范围、配置口径和高成本工作边界已经由agent冻结并留存版本记录']

### s03 数据对齐、样本构建与最小干运行
- desc: 按冻结方案完成时间、空间、变量、单位和质量标志对齐，建立开发与独立验证样本，并在目标环境完成最小干运行。
- depend: ['s02']
- prompt: 仅在s02任务配置冻结门禁通过后执行。{HIGH_RES_TEMPERATURE_REFERENCE}、{VERTICAL_COORDINATE_SPEC}、{DATA_ALIGNMENT_SPEC}、{SAMPLE_SPLIT_SPEC}均为可选输入：未提供的规则或方案字段由agent依据s02冻结方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。按{HIGH_RES_TEMPERATURE_REFERENCE}、{VERTICAL_COORDINATE_SPEC}、{DATA_ALIGNMENT_SPEC}和{SAMPLE_SPLIT_SPEC}对齐三维海温、SST观测、气象强迫和高分辨率参考，建立无泄漏样本。完成对齐与样本构建后，运行s02冻结的最小案例，实际验证数据读取、核心计算或模型构建与加载、单批次前向或短流程以及结果写出，并保存输入快照、配置和日志；最小干运行不得作为精度或业务性能通过证据。
- step_input:
  - {HIGH_RES_TEMPERATURE_REFERENCE} (required=False, type=str, var_name=高分辨率海温参考, hint=输入独立海温参考路径。, default=None)
  - {VERTICAL_COORDINATE_SPEC} (required=False, type=str, var_name=垂向坐标规格, hint=输入层次深度定义。, default=None)
  - {DATA_ALIGNMENT_SPEC} (required=False, type=str, var_name=数据对齐规格, hint=可输入已冻结对齐规则。, default=None)
  - {SAMPLE_SPLIT_SPEC} (required=False, type=str, var_name=样本划分规格, hint=可输入已冻结划分规则。, default=None)
- outputs: ['对齐后的模型数据集', '开发—调参—独立验证样本索引', '数据质量、处理记录和最小干运行日志']
- quality_gate: ['时间、空间、变量、单位和坐标语义一致', '方法构建或配置、参数选择和独立验证资料用途隔离且无时间或空间泄漏', '缺测、异常、插补和剔除均有记录，处理前后数据可追溯', '最小干运行满足输入输出契约并无异常数值', '模型、依赖、GPU环境和数据接口兼容', '本步骤声明的全部必要外部数据、基础模型工件（如适用）和软件依赖均已实际获得、可读且版本冻结；只有获取方案而尚未取得本步骤必要输入时，本步骤不得通过']

### s04 海温订正降尺度模型训练与产品生成
- desc: 融合海温数值预报、海表观测和气象强迫，生成未来7天1 km逐小时三维海温产品。
- depend: ['s03']
- prompt: 仅在s02任务配置冻结门禁和s03数据与干运行门禁均通过后执行；否则停止并标记BLOCKED。执行前核验本步骤全部输入值或路径已提供；对文件和数据类输入，核验其实际存在、可读、获准使用且与s03冻结的数据契约一致，并记录版本与校验信息；缺失或不一致时停止并标记BLOCKED。按s02冻结方案训练并运行海温订正降尺度模型，以{FORECAST_START_TIME}生成{FORECAST_HORIZON}、{OUTPUT_INTERVAL}间隔的1 km三维海温产品至{OUTPUT_DIRECTORY}，保留原始—改进对应、模型身份和日志。
- step_input:
  - {FORECAST_START_TIME} (required=True, type=str, var_name=起报时间, hint=输入UTC起报时间。, default=None)
  - {FORECAST_HORIZON} (required=True, type=str, var_name=预报时效, hint=输入目标预报时效。, default=未来7天)
  - {OUTPUT_INTERVAL} (required=True, type=str, var_name=输出时间间隔, hint=输入产品时间间隔。, default=1小时)
  - {OUTPUT_DIRECTORY} (required=True, type=str, var_name=结果输出目录, hint=输入产品输出目录。, default=None)
- outputs: ['海温订正与降尺度模型及权重', '未来7天1km逐小时三维海温产品', '原始—改进索引、日志和产品清单']
- quality_gate: ['推理输入均在对应起报时刻可获得', '输出覆盖未来7天、水平1 km、逐小时和s02冻结的全部垂向层次', '细尺度结构具有独立高分辨率资料支持并通过质控', '原始与改进产品在变量、深度、有效时刻和单位上可对应']

### s05 产品质控与运行性能检查
- desc: 检查产品完整性、物理与统计合理性、时空连续性、异常和目标GPU环境下的运行性能。
- depend: ['s04']
- prompt: {PRODUCT_QC_SPEC}、{RUNTIME_PROTOCOL}、{FINE_SCALE_QC_SPEC}均为可选输入：未提供的规则或方案字段由agent依据s02冻结方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。依据{PRODUCT_QC_SPEC}和{FINE_SCALE_QC_SPEC}检查层次、单位、海陆边界、空间细节、时序连续性和异常，并按{RUNTIME_PROTOCOL}测量目标GPU运行性能。
- step_input:
  - {PRODUCT_QC_SPEC} (required=False, type=str, var_name=产品质控规格, hint=输入产品质控规则。, default=None)
  - {RUNTIME_PROTOCOL} (required=False, type=str, var_name=运行计时协议, hint=输入硬件与计时边界。, default=None)
  - {FINE_SCALE_QC_SPEC} (required=False, type=str, var_name=细尺度质控规格, hint=输入空间细节检查规则。, default=None)
- outputs: ['产品完整性与异常报告', '物理和统计质控报告', 'GPU运行性能报告']
- quality_gate: ['产品变量、单位、坐标、有效时间和质量标志完整', '缺测、重复、跳变、越界和不合理值已定位并记录', '运行性能使用冻结后的目标硬件、数据规模和计时边界测量', '质控失败的产品未进入正式验收样本']

### s06 独立评估与交付判定
- desc: 使用冻结的独立资料和同协议基线完成分层评估、试运行汇总、交付判定和复现归档。
- depend: ['s05']
- prompt: {BASELINE_PRODUCTS}、{ACCEPTANCE_PROTOCOL}、{IMPROVEMENT_PROTOCOL}均为可选输入：未提供的规则或方案字段由agent依据s02冻结验收方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。使用{INDEPENDENT_VALIDATION_DATA}、{BASELINE_PRODUCTS}、{IMPROVEMENT_PROTOCOL}和{ACCEPTANCE_PROTOCOL}按深度、区域和提前期比较原预报与1 km产品，核验改善≥30%和表层误差。
- step_input:
  - {INDEPENDENT_VALIDATION_DATA} (required=True, type=str, var_name=独立验证资料, hint=输入独立验证资料路径。, default=None)
  - {BASELINE_PRODUCTS} (required=False, type=str, var_name=同协议基线产品, hint=输入基线产品路径。, default=None)
  - {ACCEPTANCE_PROTOCOL} (required=False, type=str, var_name=验收协议, hint=输入指标公式和门限。, default=None)
  - {IMPROVEMENT_PROTOCOL} (required=False, type=str, var_name=海温改善协议, hint=输入30%改善计算规则。, default=None)
- outputs: ['分区域分变量分时效评估报告', '基线比较与试运行报告', '逐项验收判定与完整交付清单']
- quality_gate: ['独立验证资料未参与训练、调参或阈值选择', '模型与基线使用相同样本、区域、变量、网格和指标协议', '每个性能结论均可定位到样本、公式、产品和日志证据', '必要数据仍缺失或无法形成科学上可辩护唯一口径的项目未标记为PASS', '源代码、模型、产品、文档和复现包均可重新读取']

## 使用本工作流的场景（场景→工作流映射）
- E103
