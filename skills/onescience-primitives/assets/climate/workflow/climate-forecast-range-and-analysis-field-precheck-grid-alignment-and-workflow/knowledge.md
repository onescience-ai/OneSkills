# 工作流：climate-forecast-range-and-analysis-field-precheck-grid-alignment-and-workflow

- domain: climate
- 步骤数: 6
- 共用场景数: 1

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 起报范围与分析场预检
- desc: 固定起报时间、预报时效和变量范围，核验全球分析场的时次、层次、单位、坐标、缺测与资料截止时间。
- depend: []
- prompt: 读取{INITIAL_ANALYSIS}，以{FORECAST_START_TIME}为起报时间、{LEAD_DAYS}天为目标时效，核验{VARIABLES_AND_LEVELS}和{DATA_CUTOFF_TIME}。逐项报告时次、层次、单位、网格、缺测和异常；发现未来资料泄漏、关键时次缺失或变量不兼容时停止并标记BLOCKED。
- step_input:
  - {INITIAL_ANALYSIS} (required=True, type=str, var_name=全球分析初场, hint=输入ERA5或业务分析场路径。, default=None)
  - {FORECAST_START_TIME} (required=True, type=str, var_name=起报时间, hint=输入UTC起报时间。, default=None)
  - {LEAD_DAYS} (required=True, type=str, var_name=预报步长, hint=输入待预报的步长。, default=1)
  - {VARIABLES_AND_LEVELS} (required=True, type=str, var_name=变量与层次, hint=输入变量名称和气压层。, default=None)
  - {DATA_CUTOFF_TIME} (required=True, type=str, var_name=资料截止时间, hint=输入资料截止时间。, default=None)
- outputs: ['输入文件与资料截止时间清单', '变量—层次—单位矩阵', '分析初场预检报告']
- quality_gate: ['所有动态输入的有效时间均不晚于起报时间', '输入时次数量满足所选模型的单时次或双时次要求', '必需变量、层次、单位和坐标均可识别', '缺测、重复时次和异常值已记录且未擅自补造']

### s02 网格对齐与输入标准化
- desc: 依据版本化模型输入契约执行重网格、变量排序、单位换算、标准化及静态地理特征编码。
- depend: ['s01']
- prompt: 根据{MODEL_INPUT_SPEC}和{PREPROCESS_CONFIG}处理通过预检的分析场，执行{MISSING_VALUE_POLICY}，生成与模型严格兼容的输入张量。记录每项重网格、单位换算、变量排序和标准化参数，保证处理可追溯。
- step_input:
  - {MODEL_INPUT_SPEC} (required=True, type=str, var_name=模型输入规格, hint=输入模型类型，如Swin-transformer、GNN、AFNO。, default=None)
  - {PREPROCESS_CONFIG} (required=True, type=str, var_name=预处理配置, hint=输入预处理配置路径。, default=None)
  - {MISSING_VALUE_POLICY} (required=True, type=str, var_name=缺测处理策略, hint=输入拒绝或插补策略。, default=None)
- outputs: ['标准化模型输入张量', '输入掩膜与静态特征', '预处理转换清单']
- quality_gate: ['张量维度、变量顺序、时次顺序和坐标方向与模型输入契约一致', '经度周期、极点、日历和气压层顺序已核验', '归一化参数与检查点版本一致', '不存在模型不支持的NaN或Inf']

### s03 模型与检查点兼容性验证
- desc: 加载模型代码、配置和检查点，核验版本、哈希、输入输出通道并执行单步干运行。
- depend: ['s01']
- prompt: 加载{MODEL_CONFIG}和{MODEL_CHECKPOINT}，核对{CHECKPOINT_SHA256}，在{RUNTIME_DEVICE}上执行一个原生时间步的干运行。报告代码、依赖、配置和权重版本；存在通道错配、缺失权重或未登记转换时停止。
- step_input:
  - {MODEL_CHECKPOINT} (required=True, type=str, var_name=模型权重路径, hint=输入模型权重文件路径。, default=None)
  - {MODEL_CONFIG} (required=True, type=str, var_name=模型配置路径, hint=输入模型配置文件路径。, default=None)
  - {CHECKPOINT_SHA256} (required=False, type=str, var_name=权重SHA-256, hint=输入权重SHA-256。, default=None)
  - {RUNTIME_DEVICE} (required=True, type=str, var_name=推理设备, hint=输入运行设备，如GPU。, default=None)
- outputs: ['模型与检查点身份报告', '输入输出兼容性矩阵', '单步干运行日志']
- quality_gate: ['检查点SHA-256与登记值一致', '代码、配置、标准化参数和检查点属于兼容版本', '不存在缺失或意外的权重、变量和通道', '单步干运行正常退出且输出形状和值域可检查']

### s04 1—10天确定性状态滚动
- desc: 按模型原生推进方式生成目标时段内的全球多变量确定性预报轨迹。
- depend: ['s02', 's03']
- prompt: 采用{ROLLOUT_STRATEGY}，以{OUTPUT_INTERVAL_HOURS}小时为间隔，把标准化初场推进至{LEAD_DAYS}天。按{SAVE_INTERMEDIATE_STATES}保存中间状态并固定{RANDOM_SEED}；逐步记录有效时刻、输入来源、输出形状、数值范围、耗时和资源占用。
- step_input:
  - {ROLLOUT_STRATEGY} (required=True, type=str, var_name=状态推进策略, hint=输入自回归或多时效推进。, default=None)
  - {OUTPUT_INTERVAL_HOURS} (required=True, type=str, var_name=输出时间间隔, hint=输入输出间隔，单位小时。, default=6)
  - {SAVE_INTERMEDIATE_STATES} (required=False, type=str, var_name=保存中间状态, hint=输入是否保存中间状态。, default=true)
  - {RANDOM_SEED} (required=False, type=str, var_name=运行随机种子, hint=输入随机种子。, default=None)
- outputs: ['标准化全球确定性预报序列', '中间状态检查点', '推理日志与资源统计']
- quality_gate: ['目标时段内预报时次完整且不存在重复、跳步或时间错位', '所有输出的维度、变量顺序和坐标与模型契约一致', '每一步输出均不存在NaN或Inf', '滚动过程中未读取起报时间之后的分析或验证资料', '断点续算未混用不同检查点、配置或预处理版本']

### s05 物理量恢复与产品生成
- desc: 执行反标准化、单位恢复和必要的网格转换，生成带完整时空坐标与版本元数据的多变量产品。
- depend: ['s04']
- prompt: 将预报序列反标准化并恢复物理单位，按{OUTPUT_GRID}和{OUTPUT_FORMAT}写入{OUTPUT_DIRECTORY}。仅生成可由现有变量和明确公式得到的{DERIVED_PRODUCTS}，同时写入起报时间、有效时间、模型、检查点、配置、变量、单位和处理历史。
- step_input:
  - {OUTPUT_GRID} (required=True, type=str, var_name=交付网格, hint=输入目标网格。, default=None)
  - {OUTPUT_FORMAT} (required=True, type=str, var_name=输出格式, hint=输入NetCDF、Zarr或GRIB2。, default=None)
  - {DERIVED_PRODUCTS} (required=False, type=str, var_name=派生产品, hint=输入派生产品，逗号分隔。, default=None)
  - {OUTPUT_DIRECTORY} (required=True, type=str, var_name=结果保存路径, hint=输入预报结果保存路径。, default=None)
- outputs: ['全球多层多变量确定性预报场', '经明确配置的派生产品', '产品元数据与文件清单']
- quality_gate: ['反标准化参数与输入预处理版本严格对应', '变量单位、物理范围、坐标、日历和有效时间已核验', '输出文件能够重新打开且维度、变量和元数据完整', '派生变量均有明确公式和源变量']

### s06 同协议检验与交付判定
- desc: 验证资料可用时按变量、层次、区域和时效计算确定性技巧，并与同条件基线比较。
- depend: ['s05']
- prompt: 若{VERIFICATION_REFERENCE}可用，依据{VALIDATION_PROTOCOL}计算{METRICS}，并在同起报、同参考和同网格条件下比较{BENCHMARK_FORECAST}；同时检查频谱、预报活动度、异常极值和长滚动稳定性。资料或门限缺失时不得用论文结果替代本次验证。
- step_input:
  - {VERIFICATION_REFERENCE} (required=False, type=str, var_name=独立验证资料, hint=输入验证资料路径。, default=None)
  - {BENCHMARK_FORECAST} (required=False, type=str, var_name=基线预报, hint=输入基线预报路径。, default=None)
  - {METRICS} (required=True, type=str, var_name=检验指标, hint=输入检验指标，逗号分隔。, default=None)
  - {VALIDATION_PROTOCOL} (required=False, type=str, var_name=验证与验收协议, hint=输入验收协议路径。, default=None)
- outputs: ['分变量分层分区域分时效技能报告', '同协议基线比较报告', '频谱、活动度与稳定性诊断', '质量判定与交付清单']
- quality_gate: ['预报、基线和参考资料采用一致的起报时间、网格和面积权重', '验证资料未参与本次模型输入或参数选择', '指标按变量、层次、区域和时效分层报告', '只有达到预先登记的验收门限才能判定性能PASS', '验证资料或门限缺失时不作性能通过声明', '配置、命令、退出码、日志、产物路径和文件哈希可追溯']

## 使用本工作流的场景（场景→工作流映射）
- E1
