# 工作流：climate-scenario-forcing-task-boundary-precheck-scenario-forcing-workflow

- domain: climate
- 步骤数: 6
- 共用场景数: 1

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 情景外强迫及任务边界预检
- desc: 界定“给定边界强迫的全球大气气候轨迹代理模拟”的任务范围并执行“情景外强迫及任务边界预检”，核验海温、太阳辐射、地形及初始大气状态的来源、覆盖、有效时间和可用边界。
- depend: []
- prompt: 面向“给定边界强迫的全球大气气候轨迹代理模拟”，读取{BOUNDARY_FORCING}、{SCENARIO_DEFINITION}、{SIMULATION_PERIOD}、{REFERENCE_PERIOD}并完成情景外强迫及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- step_input:
  - {BOUNDARY_FORCING} (required=True, type=str, var_name=边界与外强迫, hint=输入边界和强迫资料路径。, default=None)
  - {SCENARIO_DEFINITION} (required=True, type=str, var_name=情景定义, hint=输入气候情景定义。, default=None)
  - {SIMULATION_PERIOD} (required=True, type=str, var_name=模拟时段, hint=输入模拟起止时间。, default=None)
  - {REFERENCE_PERIOD} (required=True, type=str, var_name=异常基准期, hint=输入异常基准时段。, default=None)
- outputs: ['输入数据与版本清单', '任务范围和资料截止时间表', '输入完整性预检报告']
- quality_gate: ['所有必需输入均存在且路径、版本和来源可追溯', '任务区域、时段、变量和输出目标无歧义', '缺测、重复和异常资料已记录且未擅自补造', '外强迫、情景、日历和基准期定义可追溯']

### s02 情景外强迫时空对齐与样本构造
- desc: 执行“情景外强迫时空对齐与样本构造”，统一海温、太阳辐射、地形及初始大气状态的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- depend: ['s01']
- prompt: 依据{CALENDAR_AND_GRID}、{PREPROCESS_CONFIG}、{SPLIT_PROTOCOL}完成情景外强迫时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。
- step_input:
  - {CALENDAR_AND_GRID} (required=True, type=str, var_name=日历与网格, hint=输入日历和网格规格。, default=None)
  - {PREPROCESS_CONFIG} (required=True, type=str, var_name=预处理配置, hint=输入预处理配置。, default=None)
  - {SPLIT_PROTOCOL} (required=True, type=str, var_name=回报划分协议, hint=输入按年份划分协议。, default=None)
- outputs: ['对齐后的标准输入', '掩膜与样本索引', '预处理转换记录']
- quality_gate: ['预处理后的时间轴、坐标、单位和形状可检查', '每项插值、归一化、掩膜和缺测处理均有记录', '不存在由验证资料或未来资料造成的信息泄漏', '回报或验证年份未参与参数选择']

### s03 方法配置与输入输出契约验证
- desc: 执行“方法配置与输入输出契约验证”，冻结方法工件、参数和随机性配置，并以小样本检查输入输出契约。
- depend: ['s02']
- prompt: 依据{METHOD_ARTIFACT}、{METHOD_CONFIG}、{RANDOM_SEED}加载方法工件与配置并完成方法配置与输入输出契约验证。核对变量顺序、张量或表结构、目标定义和输出契约，执行最小干运行；版本不匹配、出现缺失字段或异常数值时停止并标记BLOCKED。
- step_input:
  - {METHOD_ARTIFACT} (required=True, type=str, var_name=方法工件, hint=输入方法工件路径。, default=None)
  - {METHOD_CONFIG} (required=True, type=str, var_name=方法配置, hint=输入方法参数配置。, default=None)
  - {RANDOM_SEED} (required=True, type=str, var_name=随机种子, hint=输入可复现实验种子。, default=0)
- outputs: ['方法工件与配置身份报告', '输入输出兼容性矩阵', '最小干运行日志']
- quality_gate: ['方法工件、配置和运行环境属于兼容版本', '目标变量和输出结构与任务定义一致', '最小干运行正常退出且结果不存在NaN或Inf', '回报或验证年份未参与参数选择']

### s04 在给定强迫下多年自由积分
- desc: 按冻结配置执行“在给定强迫下多年自由积分”，完成从海温、太阳辐射、地形及初始大气状态到多年全球大气场、降水和能量水分通量的核心计算并保存逐阶段日志。
- depend: ['s03']
- prompt: 依据{RUN_CONFIG}、{ENSEMBLE_SIZE}、{OUTPUT_FREQUENCY}执行在给定强迫下多年自由积分，将海温、太阳辐射、地形及初始大气状态转换为多年全球大气场、降水和能量水分通量。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。
- step_input:
  - {RUN_CONFIG} (required=True, type=str, var_name=运行配置, hint=输入运行参数配置。, default=None)
  - {ENSEMBLE_SIZE} (required=True, type=str, var_name=集合成员数, hint=输入集合成员数量。, default=1)
  - {OUTPUT_FREQUENCY} (required=True, type=str, var_name=输出频率, hint=输入结果输出频率。, default=None)
- outputs: ['在给定强迫下多年自由积分结果', '中间状态与运行日志', '资源和退出状态记录']
- quality_gate: ['目标区域和时段内结果完整且无重复或错位', '核心计算未读取任务截止时间之后的数据', '配置、随机种子、日志和中间状态能够追溯', '长期积分无非物理漂移或未解释的数值突变']

### s05 结果恢复与场景产品生成
- desc: 执行“结果恢复与场景产品生成”，恢复物理量、坐标和元数据，生成多年全球大气场、降水和能量水分通量及必要的质量标志。
- depend: ['s04']
- prompt: 依据{OUTPUT_FORMAT}、{OUTPUT_DIRECTORY}、{POSTPROCESS_CONFIG}、{DERIVED_PRODUCTS}完成结果恢复与场景产品生成，对核心结果执行已登记的校准、订正、派生或聚合并输出多年全球大气场、降水和能量水分通量。核验单位、坐标、时次、无效值、物理范围和文件可读性；派生量必须记录公式和源变量。
- step_input:
  - {OUTPUT_FORMAT} (required=True, type=str, var_name=输出格式, hint=输入输出文件格式。, default=None)
  - {OUTPUT_DIRECTORY} (required=True, type=str, var_name=结果保存路径, hint=输入结果保存路径。, default=None)
  - {POSTPROCESS_CONFIG} (required=False, type=str, var_name=后处理配置, hint=输入订正派生聚合配置。, default=None)
  - {DERIVED_PRODUCTS} (required=False, type=str, var_name=派生产品, hint=输入派生产品清单。, default=None)
- outputs: ['多年全球大气场、降水和能量水分通量', '质量标志与不确定性信息', '产品元数据与文件清单']
- quality_gate: ['输出文件能够重新打开且变量和元数据完整', '结果单位、坐标、有效时间和物理范围已核验', '派生产品均有明确公式、源变量和质量标志', '长期积分无非物理漂移或未解释的数值突变']

### s06 检查漂移、守恒和极端统计
- desc: 执行“检查漂移、守恒和极端统计”，使用未参与参数选择的参考资料检验多年全球大气场、降水和能量水分通量，给出适用范围与交付判定。
- depend: ['s05']
- prompt: 依据{VERIFICATION_REFERENCE}、{BENCHMARK_RESULT}、{METRICS}、{ACCEPTANCE_CRITERIA}以独立参考资料完成检查漂移、守恒和极端统计。按预先登记的区域、时段、事件或提前期计算指标并与同协议基线比较；缺少参考资料或验收门限时只能报告结果，不得声明性能PASS。
- step_input:
  - {VERIFICATION_REFERENCE} (required=True, type=str, var_name=独立验证资料, hint=输入独立验证资料路径。, default=None)
  - {BENCHMARK_RESULT} (required=False, type=str, var_name=基线结果, hint=输入同协议基线结果。, default=None)
  - {METRICS} (required=True, type=str, var_name=检验指标, hint=输入检验指标，逗号分隔。, default=None)
  - {ACCEPTANCE_CRITERIA} (required=False, type=str, var_name=验收门限, hint=输入预先登记的门限。, default=None)
- outputs: ['分层检验指标报告', '同协议基线比较报告', '适用边界与交付判定']
- quality_gate: ['验证资料未参与训练、参数选择或阈值调优', '结果与基线采用相同样本、网格和指标协议', '未达到预先登记门限时不得判定性能通过', '配置、日志、产物路径和文件哈希可追溯', '均值、变率、极端和空间结构均分层检验']

## 使用本工作流的场景（场景→工作流映射）
- E57
