# 工作流：climate-hydro-forcing-basin-data-boundary-precheck-hydro-forcing-basin-workflow-9

- domain: climate
- 步骤数: 6
- 共用场景数: 1

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 水文强迫和流域资料及任务边界预检
- desc: 界定“流域气象干旱指数的月季尺度预报”的任务范围并执行“水文强迫和流域资料及任务边界预检”，核验历史气象序列、气候因子的来源、覆盖、有效时间和可用边界。
- depend: []
- prompt: 面向“流域气象干旱指数的月季尺度预报”，读取{METEOROLOGICAL_FORCING}、{BASIN_ATTRIBUTES}、{HYDROLOGICAL_OBSERVATIONS}、{SIMULATION_PERIOD}、{DATA_CUTOFF_TIME}并完成水文强迫和流域资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- step_input:
  - {METEOROLOGICAL_FORCING} (required=True, type=str, var_name=气象强迫资料, hint=输入气象强迫资料路径。, default=None)
  - {BASIN_ATTRIBUTES} (required=True, type=str, var_name=流域属性资料, hint=输入流域属性资料路径。, default=None)
  - {HYDROLOGICAL_OBSERVATIONS} (required=False, type=str, var_name=水文观测资料, hint=输入水文观测资料路径。, default=None)
  - {SIMULATION_PERIOD} (required=True, type=str, var_name=模拟预报时段, hint=输入处理起止时间。, default=None)
  - {DATA_CUTOFF_TIME} (required=True, type=str, var_name=资料截止时间, hint=输入资料截止时间。, default=None)
- outputs: ['输入数据与版本清单', '任务范围和资料截止时间表', '输入完整性预检报告']
- quality_gate: ['所有必需输入均存在且路径、版本和来源可追溯', '任务区域、时段、变量和输出目标无歧义', '缺测、重复和异常资料已记录且未擅自补造', '气象强迫、流域边界和水文观测时空一致']

### s02 水文强迫和流域资料时空对齐与样本构造
- desc: 执行“水文强迫和流域资料时空对齐与样本构造”，统一历史气象序列、气候因子的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- depend: ['s01']
- prompt: 依据{TIME_RESOLUTION}、{SPATIAL_MAPPING}、{WARMUP_POLICY}、{MISSING_VALUE_POLICY}完成水文强迫和流域资料时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。
- step_input:
  - {TIME_RESOLUTION} (required=True, type=str, var_name=时间分辨率, hint=输入时间分辨率。, default=None)
  - {SPATIAL_MAPPING} (required=True, type=str, var_name=空间映射配置, hint=输入流域空间映射配置。, default=None)
  - {WARMUP_POLICY} (required=False, type=str, var_name=预热期规则, hint=输入状态预热规则。, default=None)
  - {MISSING_VALUE_POLICY} (required=True, type=str, var_name=缺测处理规则, hint=输入缺测处理规则。, default=None)
- outputs: ['对齐后的标准输入', '掩膜与样本索引', '预处理转换记录']
- quality_gate: ['预处理后的时间轴、坐标、单位和形状可检查', '每项插值、归一化、掩膜和缺测处理均有记录', '不存在由验证资料或未来资料造成的信息泄漏', '训练验证按时间或流域隔离并防止未来泄漏']

### s03 方法配置与输入输出契约验证
- desc: 执行“方法配置与输入输出契约验证”，冻结方法工件、参数和随机性配置，并以小样本检查输入输出契约。
- depend: ['s02']
- prompt: 依据{METHOD_ARTIFACT}、{METHOD_CONFIG}、{RANDOM_SEED}加载方法工件与配置并完成方法配置与输入输出契约验证。核对变量顺序、张量或表结构、目标定义和输出契约，执行最小干运行；版本不匹配、出现缺失字段或异常数值时停止并标记BLOCKED。
- step_input:
  - {METHOD_ARTIFACT} (required=True, type=str, var_name=方法工件, hint=输入方法工件路径。, default=None)
  - {METHOD_CONFIG} (required=True, type=str, var_name=方法配置, hint=输入方法参数配置。, default=None)
  - {RANDOM_SEED} (required=True, type=str, var_name=随机种子, hint=输入可复现实验种子。, default=0)
- outputs: ['方法工件与配置身份报告', '输入输出兼容性矩阵', '最小干运行日志']
- quality_gate: ['方法工件、配置和运行环境属于兼容版本', '目标变量和输出结构与任务定义一致', '最小干运行正常退出且结果不存在NaN或Inf', '训练验证按时间或流域隔离并防止未来泄漏']

### s04 滚动预测干旱指数
- desc: 按冻结配置执行“滚动预测干旱指数”，完成从历史气象序列、气候因子到SPI等干旱指数、等级与发生概率的核心计算并保存逐阶段日志。
- depend: ['s03']
- prompt: 依据{RUN_CONFIG}、{INITIAL_STATE}、{ENSEMBLE_SIZE}执行滚动预测干旱指数，将历史气象序列、气候因子转换为SPI等干旱指数、等级与发生概率。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。
- step_input:
  - {RUN_CONFIG} (required=True, type=str, var_name=运行配置, hint=输入运行参数配置。, default=None)
  - {INITIAL_STATE} (required=False, type=str, var_name=初始水文状态, hint=输入初始水文状态路径。, default=None)
  - {ENSEMBLE_SIZE} (required=True, type=str, var_name=集合成员数, hint=输入集合成员数量。, default=1)
- outputs: ['滚动预测干旱指数结果', '中间状态与运行日志', '资源和退出状态记录']
- quality_gate: ['目标区域和时段内结果完整且无重复或错位', '核心计算未读取任务截止时间之后的数据', '配置、随机种子、日志和中间状态能够追溯', '水量、状态范围和洪峰时序不存在非物理异常']

### s05 结果恢复与场景产品生成
- desc: 执行“结果恢复与场景产品生成”，恢复物理量、坐标和元数据，生成SPI等干旱指数、等级与发生概率及必要的质量标志。
- depend: ['s04']
- prompt: 依据{OUTPUT_FORMAT}、{OUTPUT_DIRECTORY}、{POSTPROCESS_CONFIG}、{DERIVED_PRODUCTS}完成结果恢复与场景产品生成，对核心结果执行已登记的校准、订正、派生或聚合并输出SPI等干旱指数、等级与发生概率。核验单位、坐标、时次、无效值、物理范围和文件可读性；派生量必须记录公式和源变量。
- step_input:
  - {OUTPUT_FORMAT} (required=True, type=str, var_name=输出格式, hint=输入输出文件格式。, default=None)
  - {OUTPUT_DIRECTORY} (required=True, type=str, var_name=结果保存路径, hint=输入结果保存路径。, default=None)
  - {POSTPROCESS_CONFIG} (required=False, type=str, var_name=后处理配置, hint=输入订正派生聚合配置。, default=None)
  - {DERIVED_PRODUCTS} (required=False, type=str, var_name=派生产品, hint=输入派生产品清单。, default=None)
- outputs: ['SPI等干旱指数、等级与发生概率', '质量标志与不确定性信息', '产品元数据与文件清单']
- quality_gate: ['输出文件能够重新打开且变量和元数据完整', '结果单位、坐标、有效时间和物理范围已核验', '派生产品均有明确公式、源变量和质量标志', '水量、状态范围和洪峰时序不存在非物理异常']

### s06 按时间外样本验证
- desc: 执行“按时间外样本验证”，使用未参与参数选择的参考资料检验SPI等干旱指数、等级与发生概率，给出适用范围与交付判定。
- depend: ['s05']
- prompt: 依据{VERIFICATION_REFERENCE}、{BENCHMARK_RESULT}、{METRICS}、{ACCEPTANCE_CRITERIA}以独立参考资料完成按时间外样本验证。按预先登记的区域、时段、事件或提前期计算指标并与同协议基线比较；缺少参考资料或验收门限时只能报告结果，不得声明性能PASS。
- step_input:
  - {VERIFICATION_REFERENCE} (required=True, type=str, var_name=独立验证资料, hint=输入独立验证资料路径。, default=None)
  - {BENCHMARK_RESULT} (required=False, type=str, var_name=基线结果, hint=输入同协议基线结果。, default=None)
  - {METRICS} (required=True, type=str, var_name=检验指标, hint=输入检验指标，逗号分隔。, default=None)
  - {ACCEPTANCE_CRITERIA} (required=False, type=str, var_name=验收门限, hint=输入预先登记的门限。, default=None)
- outputs: ['分层检验指标报告', '同协议基线比较报告', '适用边界与交付判定']
- quality_gate: ['验证资料未参与训练、参数选择或阈值调优', '结果与基线采用相同样本、网格和指标协议', '未达到预先登记门限时不得判定性能通过', '配置、日志、产物路径和文件哈希可追溯', '综合径流、高低流和洪峰指标分层报告']

## 使用本工作流的场景（场景→工作流映射）
- E18
