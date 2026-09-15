# 工作流：wf-climate-378718a7

- domain: climate
- 步骤数: 6
- 共用场景数: 1

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 模型输入与运行条件预检
- desc: 核对模型实际输入的数据身份、版本、权限、资料截止时间、变量、时空覆盖和缺测，形成输入清单与数据阻断项。
- depend: []
- prompt: 读取{OCEAN_INITIAL_STATE}、{OCEAN_FORCING_DATA}、{OCEAN_BOUNDARY_DATA}和{BATHYMETRY_DATA}，以{DATA_CUTOFF_TIME}核验北海区覆盖、变量、层次、时次、边界、基准和缺测；缺少必需输入时标记BLOCKED。
- step_input:
  - {OCEAN_INITIAL_STATE} (required=True, type=str, var_name=三维海洋初始场, hint=输入温盐流初始场路径。, default=None)
  - {OCEAN_FORCING_DATA} (required=True, type=str, var_name=海洋外部强迫, hint=输入气象潮汐强迫路径。, default=None)
  - {OCEAN_BOUNDARY_DATA} (required=True, type=str, var_name=开放边界数据, hint=输入区域边界场路径。, default=None)
  - {BATHYMETRY_DATA} (required=True, type=str, var_name=海底地形数据, hint=输入海底地形路径。, default=None)
  - {DATA_CUTOFF_TIME} (required=True, type=str, var_name=资料截止时间, hint=输入资料截止时间。, default=None)
- outputs: ['输入数据与版本清单', '输入时空变量与缺测检查报告', '数据缺失、权限和契约阻断项']
- quality_gate: ['输入文件存在、可读、获准使用且来源和版本可追溯', '输入的区域、时段、网格、变量、单位、坐标和资料截止时间已逐项核对', '未来资料、模型开发资料和独立验证资料的用途已隔离', '输入数据中的缺失、冲突和异常未被推测值覆盖']

### s02 执行方案设计与任务配置冻结
- desc: 由agent根据预检结果形成方法、数据、资源、验证和失败分支方案，冻结任务范围、运行配置与验收口径。
- depend: ['s01']
- prompt: {PHYSICAL_CONSTRAINT_SPEC}均为可选输入：未提供的规则或方案字段由agent依据s01预检结果形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。围绕{PHYSICAL_CONSTRAINT_SPEC}、{GPU_ENVIRONMENT}和{RESOURCE_BUDGET}提交联合温盐流方案，明确海水状态方程等约束如何嵌入神经网络并验证，定义s03最小干运行范围，并冻结1/36°含义和指标口径。将任务范围、数据契约、方法、资源、运行环境和验收协议写入版本化任务配置；关键字段无法冻结时标记BLOCKED，配置冻结后方可进入s03。
- step_input:
  - {PHYSICAL_CONSTRAINT_SPEC} (required=False, type=str, var_name=物理约束规格, hint=输入状态方程等约束。, default=None)
  - {GPU_ENVIRONMENT} (required=True, type=str, var_name=目标GPU环境, hint=输入GPU环境与调度信息。, default=None)
  - {RESOURCE_BUDGET} (required=True, type=str, var_name=资源与时间预算, hint=输入可用资源和期限。, default=None)
- outputs: ['冻结的执行与验收方案', '版本化任务配置', '资源估算、风险和失败分支']
- quality_gate: ['方案说明方法、数据和资源选择理由且未把实现细节冒充既定任务条件', '必需数据、可选数据、获取责任和缺失时的阻断条件已列明', '指标公式、基线、验证资料、样本范围和计时边界已列明', '任务范围、配置口径和高成本工作边界已经由agent冻结并留存版本记录']

### s03 数据对齐、样本构建与最小干运行
- desc: 按冻结方案完成时间、空间、变量、单位和质量标志对齐，建立开发与独立验证样本，并在目标环境完成最小干运行。
- depend: ['s02']
- prompt: 仅在s02任务配置冻结门禁通过后执行。{OCEAN_REFERENCE_DATA}、{DATA_ALIGNMENT_SPEC}、{SAMPLE_SPLIT_SPEC}均为可选输入：未提供的规则或方案字段由agent依据s02冻结方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。按{OCEAN_REFERENCE_DATA}、{VERTICAL_COORDINATE_SPEC}、{DATA_ALIGNMENT_SPEC}和{SAMPLE_SPLIT_SPEC}对齐初始场、强迫、边界、地形与参考，建立无泄漏的三维训练和独立验证样本。完成对齐与样本构建后，运行s02冻结的最小案例，实际验证数据读取、核心计算或模型构建与加载、单批次前向或短流程以及结果写出，并保存输入快照、配置和日志；最小干运行不得作为精度或业务性能通过证据。
- step_input:
  - {OCEAN_REFERENCE_DATA} (required=False, type=str, var_name=温盐流参考资料, hint=输入训练验证参考路径。, default=None)
  - {VERTICAL_COORDINATE_SPEC} (required=True, type=str, var_name=垂向坐标规格, hint=输入层次深度定义。, default=垂向不少于30层)
  - {DATA_ALIGNMENT_SPEC} (required=False, type=str, var_name=数据对齐规格, hint=可输入已冻结对齐规则。, default=None)
  - {SAMPLE_SPLIT_SPEC} (required=False, type=str, var_name=样本划分规格, hint=可输入已冻结划分规则。, default=None)
- outputs: ['对齐后的模型数据集', '开发—调参—独立验证样本索引', '数据质量、处理记录和最小干运行日志']
- quality_gate: ['时间、空间、变量、单位和坐标语义一致', '方法构建或配置、参数选择和独立验证资料用途隔离且无时间或空间泄漏', '缺测、异常、插补和剔除均有记录，处理前后数据可追溯', '最小干运行满足输入输出契约并无异常数值', '模型、依赖、GPU环境和数据接口兼容', '本步骤声明的全部必要外部数据、基础模型工件（如适用）和软件依赖均已实际获得、可读且版本冻结；只有获取方案而尚未取得本步骤必要输入时，本步骤不得通过']

### s04 三维温盐流联合模型训练与预报生成
- desc: 将海水状态方程等物理约束嵌入神经网络，生成逐小时三维温度、盐度和海流预报。
- depend: ['s03']
- prompt: 仅在s02任务配置冻结门禁和s03数据与干运行门禁均通过后执行；否则停止并标记BLOCKED。执行前核验本步骤全部输入值或路径已提供；对文件和数据类输入，核验其实际存在、可读、获准使用且与s03冻结的数据契约一致，并记录版本与校验信息；缺失或不一致时停止并标记BLOCKED。按s02冻结方案训练并运行三维温盐流模型，以{FORECAST_START_TIME}生成{FORECAST_HORIZON}、{OUTPUT_INTERVAL}间隔的温度、盐度和海流产品至{OUTPUT_DIRECTORY}，记录物理约束诊断、模型身份和日志。
- step_input:
  - {FORECAST_START_TIME} (required=True, type=str, var_name=起报时间, hint=输入UTC起报时间。, default=None)
  - {FORECAST_HORIZON} (required=True, type=str, var_name=预报时效, hint=输入目标预报时效。, default=7天)
  - {OUTPUT_INTERVAL} (required=True, type=str, var_name=输出时间间隔, hint=输入产品时间间隔。, default=1小时)
  - {OUTPUT_DIRECTORY} (required=True, type=str, var_name=结果输出目录, hint=输入产品输出目录。, default=None)
- outputs: ['三维温盐流智能预报模型与配置', '逐小时三维温度盐度海流产品', '物理诊断、运行日志和产品清单']
- quality_gate: ['温度、盐度和海流全部按s02冻结网格与不少于30层输出', '初始场、强迫和开放边界在每个有效时次正确对齐', '物理约束实现和诊断结果可复核', '预报覆盖s02冻结时效且输出间隔为1小时']

### s05 产品质控与运行性能检查
- desc: 检查产品完整性、物理与统计合理性、时空连续性、异常和目标GPU环境下的运行性能。
- depend: ['s04']
- prompt: {PRODUCT_QC_SPEC}、{RUNTIME_PROTOCOL}、{PHYSICAL_QC_SPEC}均为可选输入：未提供的规则或方案字段由agent依据s02冻结方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。依据{PRODUCT_QC_SPEC}和{PHYSICAL_QC_SPEC}检查层次、单位、温盐范围、流场连续性、状态方程一致性和异常，并按{RUNTIME_PROTOCOL}测量目标GPU运行性能。
- step_input:
  - {PRODUCT_QC_SPEC} (required=False, type=str, var_name=产品质控规格, hint=输入产品质控规则。, default=None)
  - {RUNTIME_PROTOCOL} (required=False, type=str, var_name=运行计时协议, hint=输入硬件与计时边界。, default=None)
  - {PHYSICAL_QC_SPEC} (required=False, type=str, var_name=物理一致性质控, hint=输入温盐流诊断规则。, default=None)
- outputs: ['产品完整性与异常报告', '物理和统计质控报告', 'GPU运行性能报告']
- quality_gate: ['产品变量、单位、坐标、有效时间和质量标志完整', '缺测、重复、跳变、越界和不合理值已定位并记录', '运行性能使用冻结后的目标硬件、数据规模和计时边界测量', '质控失败的产品未进入正式验收样本']

### s06 独立评估与交付判定
- desc: 使用冻结的独立资料和同协议基线完成分层评估、试运行汇总、交付判定和复现归档。
- depend: ['s05']
- prompt: {BASELINE_PRODUCTS}、{ACCEPTANCE_PROTOCOL}、{OCEAN_METRIC_PROTOCOL}均为可选输入：未提供的规则或方案字段由agent依据s02冻结验收方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。使用{INDEPENDENT_VALIDATION_DATA}、{BASELINE_PRODUCTS}、{OCEAN_METRIC_PROTOCOL}和{ACCEPTANCE_PROTOCOL}按深度、区域、变量和提前期评估；重点核验7天海温RMSE<0.6℃。
- step_input:
  - {INDEPENDENT_VALIDATION_DATA} (required=True, type=str, var_name=独立验证资料, hint=输入独立验证资料路径。, default=None)
  - {BASELINE_PRODUCTS} (required=False, type=str, var_name=同协议基线产品, hint=输入基线产品路径。, default=None)
  - {ACCEPTANCE_PROTOCOL} (required=False, type=str, var_name=验收协议, hint=输入指标公式和门限。, default=None)
  - {OCEAN_METRIC_PROTOCOL} (required=False, type=str, var_name=温盐流评估协议, hint=输入各变量指标公式。, default=None)
- outputs: ['分区域分变量分时效评估报告', '基线比较与试运行报告', '逐项验收判定与完整交付清单']
- quality_gate: ['独立验证资料未参与训练、调参或阈值选择', '模型与基线使用相同样本、区域、变量、网格和指标协议', '每个性能结论均可定位到样本、公式、产品和日志证据', '必要数据仍缺失或无法形成科学上可辩护唯一口径的项目未标记为PASS', '源代码、模型、产品、文档和复现包均可重新读取']

## 使用本工作流的场景（场景→工作流映射）
- E104
