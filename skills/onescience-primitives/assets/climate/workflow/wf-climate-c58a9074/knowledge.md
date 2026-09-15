# 工作流：wf-climate-c58a9074

- domain: climate
- 步骤数: 6
- 共用场景数: 1

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 天气能源运行资料及任务边界预检
- desc: 界定“天气敏感型城市电力负荷日前概率预报”的任务范围并执行“天气能源运行资料及任务边界预检”，核验历史负荷、天气预报、日历与用户层级的来源、覆盖、有效时间和可用边界。
- depend: []
- prompt: 面向“天气敏感型城市电力负荷日前概率预报”，读取{WEATHER_FORECAST}、{LOAD_HISTORY}、{CALENDAR_FEATURES}、{HIERARCHY_METADATA}、{FORECAST_START_TIME}、{DATA_CUTOFF_TIME}并完成天气能源运行资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- step_input:
  - {WEATHER_FORECAST} (required=True, type=str, var_name=日前天气预报, hint=输入日前天气预报路径。, default=None)
  - {LOAD_HISTORY} (required=True, type=str, var_name=历史电力负荷, hint=输入历史负荷资料路径。, default=None)
  - {CALENDAR_FEATURES} (required=True, type=str, var_name=日历特征, hint=输入日历节假日特征。, default=None)
  - {HIERARCHY_METADATA} (required=True, type=str, var_name=负荷层级信息, hint=输入城市配电层级信息。, default=None)
  - {FORECAST_START_TIME} (required=True, type=str, var_name=预测签发时间, hint=输入预测签发时间。, default=None)
  - {DATA_CUTOFF_TIME} (required=True, type=str, var_name=资料截止时间, hint=输入资料截止时间。, default=None)
- outputs: ['输入数据与版本清单', '任务范围和资料截止时间表', '输入完整性预检报告']
- quality_gate: ['所有必需输入均存在且路径、版本和来源可追溯', '任务区域、时段、变量和输出目标无歧义', '缺测、重复和异常资料已记录且未擅自补造', '天气输入和设施观测在签发时均真实可用']

### s02 天气能源运行资料时空对齐与样本构造
- desc: 执行“天气能源运行资料时空对齐与样本构造”，统一历史负荷、天气预报、日历与用户层级的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- depend: ['s01']
- prompt: 依据{ALIGNMENT_CONFIG}、{HIERARCHY_CONFIG}、{MISSING_VALUE_POLICY}完成天气能源运行资料时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。
- step_input:
  - {ALIGNMENT_CONFIG} (required=True, type=str, var_name=天气负荷对齐, hint=输入天气负荷对齐配置。, default=None)
  - {HIERARCHY_CONFIG} (required=True, type=str, var_name=层级汇总配置, hint=输入层级汇总配置。, default=None)
  - {MISSING_VALUE_POLICY} (required=True, type=str, var_name=缺测处理规则, hint=输入缺测处理规则。, default=None)
- outputs: ['对齐后的标准输入', '掩膜与样本索引', '预处理转换记录']
- quality_gate: ['预处理后的时间轴、坐标、单位和形状可检查', '每项插值、归一化、掩膜和缺测处理均有记录', '不存在由验证资料或未来资料造成的信息泄漏', '容量、时区、采样间隔和缺测规则一致']

### s03 方法配置与输入输出契约验证
- desc: 执行“方法配置与输入输出契约验证”，冻结方法工件、参数和随机性配置，并以小样本检查输入输出契约。
- depend: ['s02']
- prompt: 依据{METHOD_ARTIFACT}、{METHOD_CONFIG}、{RANDOM_SEED}加载方法工件与配置并完成方法配置与输入输出契约验证。核对变量顺序、张量或表结构、目标定义和输出契约，执行最小干运行；版本不匹配、出现缺失字段或异常数值时停止并标记BLOCKED。
- step_input:
  - {METHOD_ARTIFACT} (required=True, type=str, var_name=方法工件, hint=输入方法工件路径。, default=None)
  - {METHOD_CONFIG} (required=True, type=str, var_name=方法配置, hint=输入方法参数配置。, default=None)
  - {RANDOM_SEED} (required=True, type=str, var_name=随机种子, hint=输入可复现实验种子。, default=0)
- outputs: ['方法工件与配置身份报告', '输入输出兼容性矩阵', '最小干运行日志']
- quality_gate: ['方法工件、配置和运行环境属于兼容版本', '目标变量和输出结构与任务定义一致', '最小干运行正常退出且结果不存在NaN或Inf', '容量、时区、采样间隔和缺测规则一致']

### s04 生成日前负荷分布并协调层级汇总
- desc: 按冻结配置执行“生成日前负荷分布并协调层级汇总”，完成从历史负荷、天气预报、日历与用户层级到日前负荷点值、分位数和区间的核心计算并保存逐阶段日志。
- depend: ['s03']
- prompt: 依据{RUN_CONFIG}、{QUANTILES}、{RECONCILIATION_CONFIG}执行生成日前负荷分布并协调层级汇总，将历史负荷、天气预报、日历与用户层级转换为日前负荷点值、分位数和区间。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。
- step_input:
  - {RUN_CONFIG} (required=True, type=str, var_name=负荷预测配置, hint=输入负荷预测配置。, default=None)
  - {QUANTILES} (required=True, type=str, var_name=负荷分位数, hint=输入负荷分位数清单。, default=None)
  - {RECONCILIATION_CONFIG} (required=True, type=str, var_name=层级协调配置, hint=输入层级协调配置。, default=None)
- outputs: ['生成日前负荷分布并协调层级汇总结果', '中间状态与运行日志', '资源和退出状态记录']
- quality_gate: ['目标区域和时段内结果完整且无重复或错位', '核心计算未读取任务截止时间之后的数据', '配置、随机种子、日志和中间状态能够追溯', '功率、负荷或辐照度输出满足物理边界', '先生成各层级日前负荷分布再执行层级一致性协调']

### s05 校准分位数和区间
- desc: 执行“校准分位数和区间”，恢复物理量、坐标和元数据，生成日前负荷点值、分位数和区间及必要的质量标志。
- depend: ['s04']
- prompt: 依据{OUTPUT_FORMAT}、{OUTPUT_DIRECTORY}、{POSTPROCESS_CONFIG}、{DERIVED_PRODUCTS}完成校准分位数和区间，对核心结果执行已登记的校准、订正、派生或聚合并输出日前负荷点值、分位数和区间。核验单位、坐标、时次、无效值、物理范围和文件可读性；派生量必须记录公式和源变量。
- step_input:
  - {OUTPUT_FORMAT} (required=True, type=str, var_name=输出格式, hint=输入输出文件格式。, default=None)
  - {OUTPUT_DIRECTORY} (required=True, type=str, var_name=结果保存路径, hint=输入结果保存路径。, default=None)
  - {POSTPROCESS_CONFIG} (required=False, type=str, var_name=后处理配置, hint=输入订正派生聚合配置。, default=None)
  - {DERIVED_PRODUCTS} (required=False, type=str, var_name=派生产品, hint=输入派生产品清单。, default=None)
- outputs: ['日前负荷点值、分位数和区间', '质量标志与不确定性信息', '产品元数据与文件清单']
- quality_gate: ['输出文件能够重新打开且变量和元数据完整', '结果单位、坐标、有效时间和物理范围已核验', '派生产品均有明确公式、源变量和质量标志', '功率、负荷或辐照度输出满足物理边界']

### s06 按极端温度及峰荷验证
- desc: 执行“按极端温度及峰荷验证”，使用未参与参数选择的参考资料检验日前负荷点值、分位数和区间，给出适用范围与交付判定。
- depend: ['s05']
- prompt: 依据{VERIFICATION_REFERENCE}、{BENCHMARK_RESULT}、{METRICS}、{ACCEPTANCE_CRITERIA}以独立参考资料完成按极端温度及峰荷验证。按预先登记的区域、时段、事件或提前期计算指标并与同协议基线比较；缺少参考资料或验收门限时只能报告结果，不得声明性能PASS。
- step_input:
  - {VERIFICATION_REFERENCE} (required=True, type=str, var_name=独立验证资料, hint=输入独立验证资料路径。, default=None)
  - {BENCHMARK_RESULT} (required=False, type=str, var_name=基线结果, hint=输入同协议基线结果。, default=None)
  - {METRICS} (required=True, type=str, var_name=检验指标, hint=输入检验指标，逗号分隔。, default=None)
  - {ACCEPTANCE_CRITERIA} (required=False, type=str, var_name=验收门限, hint=输入预先登记的门限。, default=None)
- outputs: ['分层检验指标报告', '同协议基线比较报告', '适用边界与交付判定']
- quality_gate: ['验证资料未参与训练、参数选择或阈值调优', '结果与基线采用相同样本、网格和指标协议', '未达到预先登记门限时不得判定性能通过', '配置、日志、产物路径和文件哈希可追溯', '与持续性和业务基线按时效及场站检验', '峰荷、极端温度日和常规日的概率技巧分别报告']

## 使用本工作流的场景（场景→工作流映射）
- E20
