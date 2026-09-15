# 工作流：wf-climate-176c48c4

- domain: climate
- 步骤数: 6
- 共用场景数: 1

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 模型输入与运行条件预检
- desc: 核对模型实际输入的数据身份、版本、权限、资料截止时间、变量、时空覆盖和缺测，形成输入清单与数据阻断项。
- depend: []
- prompt: 读取{PREDICTED_COASTAL_WATER_LEVEL}、{TERRAIN_COAST_DEFENSE}和{ADMINISTRATIVE_BOUNDARIES}，以{TARGET_COASTAL_AREA}和{DATA_CUTOFF_TIME}核验存在性、权限、水位与高程基准、坐标、空间覆盖、有效时间、岸线、防护工程和行政边界；缺少任一必要输入或关键定义时标记BLOCKED。
- step_input:
  - {PREDICTED_COASTAL_WATER_LEVEL} (required=True, type=str, var_name=预测沿岸潮位, hint=输入沿岸潮位预报路径。, default=None)
  - {TARGET_COASTAL_AREA} (required=True, type=str, var_name=目标近岸区域, hint=输入目标区域边界。, default=None)
  - {TERRAIN_COAST_DEFENSE} (required=True, type=str, var_name=地形岸线防护数据, hint=输入地形岸线工程路径。, default=None)
  - {ADMINISTRATIVE_BOUNDARIES} (required=True, type=str, var_name=行政区划数据, hint=输入行政边界数据路径。, default=None)
  - {DATA_CUTOFF_TIME} (required=True, type=str, var_name=资料截止时间, hint=输入资料截止时间。, default=None)
- outputs: ['输入数据与版本清单', '输入时空变量与缺测检查报告', '数据缺失、权限和契约阻断项']
- quality_gate: ['输入文件存在、可读、获准使用且来源和版本可追溯', '输入的区域、时段、网格、变量、单位、坐标和资料截止时间已逐项核对', '未来资料、模型开发资料和独立验证资料的用途已隔离', '输入数据中的缺失、冲突和异常未被推测值覆盖']

### s02 执行方案设计与任务配置冻结
- desc: 由agent根据预检结果形成方法、数据、资源、验证和失败分支方案，冻结任务范围、运行配置与验收口径。
- depend: ['s01']
- prompt: {INUNDATION_PRODUCT_SPEC}均为可选输入：未提供的规则或方案字段由agent依据s01预检结果形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。围绕{INUNDATION_PRODUCT_SPEC}、{GPU_ENVIRONMENT}和{RESOURCE_BUDGET}提交漫滩快速模拟、产品制作、独立验证和计时方案，并定义s03小范围干运行。将任务范围、数据契约、方法、资源、运行环境和验收协议写入版本化任务配置；关键字段无法冻结时标记BLOCKED，配置冻结后方可进入s03。
- step_input:
  - {INUNDATION_PRODUCT_SPEC} (required=False, type=str, var_name=淹没产品规格, hint=输入分辨率变量和格式。, default=None)
  - {GPU_ENVIRONMENT} (required=True, type=str, var_name=目标GPU环境, hint=输入GPU环境与调度信息。, default=None)
  - {RESOURCE_BUDGET} (required=True, type=str, var_name=资源与时间预算, hint=输入可用资源和期限。, default=None)
- outputs: ['冻结的执行与验收方案', '版本化任务配置', '资源估算、风险和失败分支']
- quality_gate: ['方案说明方法、数据和资源选择理由且未把实现细节冒充既定任务条件', '必需数据、可选数据、获取责任和缺失时的阻断条件已列明', '指标公式、基线、验证资料、样本范围和计时边界已列明', '任务范围、配置口径和高成本工作边界已经由agent冻结并留存版本记录']

### s03 空间数据对齐与运行输入构建
- desc: 按s02冻结方案对齐预测潮位、地形、岸线、防护工程和行政区划，构建运行输入与独立验证索引，并完成最小干运行。
- depend: ['s02']
- prompt: 仅在s02任务配置冻结门禁通过后执行。{DATA_ALIGNMENT_SPEC}、{SAMPLE_SPLIT_SPEC}均为可选输入：未提供的规则或方案字段由agent依据s02冻结方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。按{TERRAIN_COAST_DEFENSE}、{ADMINISTRATIVE_BOUNDARIES}、{DATA_ALIGNMENT_SPEC}和{SAMPLE_SPLIT_SPEC}对齐潮位与空间数据，检查高程基准、坐标、岸线、防护工程、行政边界和验证样本。完成对齐与样本构建后，运行s02冻结的最小案例，实际验证数据读取、核心计算或模型构建与加载、单批次前向或短流程以及结果写出，并保存输入快照、配置和日志；最小干运行不得作为精度或业务性能通过证据。
- step_input:
  - {TERRAIN_COAST_DEFENSE} (required=True, type=str, var_name=地形岸线防护数据, hint=输入s01核验通过的地形岸线工程路径。, default=None)
  - {ADMINISTRATIVE_BOUNDARIES} (required=True, type=str, var_name=行政区划数据, hint=输入s01核验通过的行政边界数据路径。, default=None)
  - {DATA_ALIGNMENT_SPEC} (required=False, type=str, var_name=数据对齐规格, hint=可输入已冻结对齐规则。, default=None)
  - {SAMPLE_SPLIT_SPEC} (required=False, type=str, var_name=样本划分规格, hint=可输入已冻结划分规则。, default=None)
- outputs: ['对齐后的潮位与空间数据', '运行输入与独立验证索引', '数据质量、处理记录和最小干运行日志']
- quality_gate: ['时间、空间、变量、单位和坐标语义一致', '方法构建或配置、参数选择和独立验证资料用途隔离且无时间或空间泄漏', '缺测、异常、插补和剔除均有记录，处理前后数据可追溯', '最小干运行满足输入输出契约并无异常数值', '模型、依赖、GPU环境和数据接口兼容', '本步骤声明的全部必要外部数据、基础模型工件（如适用）和软件依赖均已实际获得、可读且版本冻结；只有获取方案而尚未取得本步骤必要输入时，本步骤不得通过']

### s04 沿岸潮位驱动的快速淹没产品生成
- desc: 将预测沿岸潮位转换为符合s02冻结物理定义的近岸淹没分布和受影响行政区划。
- depend: ['s03']
- prompt: 仅在s02任务配置冻结门禁和s03数据与干运行门禁均通过后执行；否则停止并标记BLOCKED。执行前核验本步骤全部输入值或路径已提供；对文件和数据类输入，核验其实际存在、可读、获准使用且与s03冻结的数据契约一致，并记录版本与校验信息；缺失或不一致时停止并标记BLOCKED。按s02冻结方案处理{TARGET_WATER_LEVEL_CYCLE}，生成淹没分布图和受影响行政区划至{OUTPUT_DIRECTORY}，记录潮位批次、地形与防护版本、模型配置和日志。
- step_input:
  - {TARGET_WATER_LEVEL_CYCLE} (required=True, type=str, var_name=目标潮位批次, hint=输入本次潮位产品路径。, default=None)
  - {OUTPUT_DIRECTORY} (required=True, type=str, var_name=结果输出目录, hint=输入产品输出目录。, default=None)
- outputs: ['漫滩快速预报模型与配置', '淹没分布图和行政区划清单', '输入版本、运行日志和产品清单']
- quality_gate: ['任务范围和漫滩产品定义已经冻结', '潮位、高程、岸线、防护工程和行政边界基准一致', '淹没产品空间参考、有效时间和质量标志完整', '完整流程计时包括数据读取、模拟、制图和行政区划叠加']

### s05 产品质控与运行性能检查
- desc: 检查产品完整性、物理与统计合理性、时空连续性、异常和目标GPU环境下的运行性能。
- depend: ['s04']
- prompt: {PRODUCT_QC_SPEC}、{RUNTIME_PROTOCOL}、{SPATIAL_TOPOLOGY_SPEC}均为可选输入：未提供的规则或方案字段由agent依据s02冻结方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。依据{PRODUCT_QC_SPEC}和{SPATIAL_TOPOLOGY_SPEC}检查坐标、高程基准、淹没连通性、海陆边界和行政区划叠加，并按{RUNTIME_PROTOCOL}测量完整流程用时。
- step_input:
  - {PRODUCT_QC_SPEC} (required=False, type=str, var_name=产品质控规格, hint=输入产品质控规则。, default=None)
  - {RUNTIME_PROTOCOL} (required=False, type=str, var_name=运行计时协议, hint=输入硬件与计时边界。, default=None)
  - {SPATIAL_TOPOLOGY_SPEC} (required=False, type=str, var_name=空间拓扑规则, hint=输入连通和边界检查规则。, default=None)
- outputs: ['产品完整性与异常报告', '物理和统计质控报告', 'GPU运行性能报告']
- quality_gate: ['产品变量、单位、坐标、有效时间和质量标志完整', '缺测、重复、跳变、越界和不合理值已定位并记录', '运行性能使用冻结后的目标硬件、数据规模和计时边界测量', '质控失败的产品未进入正式验收样本']

### s06 独立评估与交付判定
- desc: 使用冻结的独立资料和同协议基线完成分层评估、试运行汇总、交付判定和复现归档。
- depend: ['s05']
- prompt: {BASELINE_PRODUCTS}、{ACCEPTANCE_PROTOCOL}、{INUNDATION_METRIC}均为可选输入：未提供的规则或方案字段由agent依据s02冻结验收方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。使用{INDEPENDENT_VALIDATION_DATA}、{BASELINE_PRODUCTS}、{INUNDATION_METRIC}和{ACCEPTANCE_PROTOCOL}评估漫滩空间结果与运行时限；缺少精度门限时，不对空间性能指标判PASS。
- step_input:
  - {INDEPENDENT_VALIDATION_DATA} (required=True, type=str, var_name=独立验证资料, hint=输入独立验证资料路径。, default=None)
  - {BASELINE_PRODUCTS} (required=False, type=str, var_name=同协议基线产品, hint=输入基线产品路径。, default=None)
  - {ACCEPTANCE_PROTOCOL} (required=False, type=str, var_name=验收协议, hint=输入指标公式和门限。, default=None)
  - {INUNDATION_METRIC} (required=False, type=str, var_name=淹没评估指标, hint=输入空间评估公式。, default=None)
- outputs: ['分区域分变量分时效评估报告', '基线比较与试运行报告', '逐项验收判定与完整交付清单']
- quality_gate: ['独立验证资料未参与训练、调参或阈值选择', '模型与基线使用相同样本、区域、变量、网格和指标协议', '每个性能结论均可定位到样本、公式、产品和日志证据', '必要数据仍缺失或无法形成科学上可辩护唯一口径的项目未标记为PASS', '源代码、模型、产品、文档和复现包均可重新读取']

## 使用本工作流的场景（场景→工作流映射）
- E109
