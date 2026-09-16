# 工作流：climate-multi-resolution-data-and-boundary-precheck-multi-resolution-workflow-4

- domain: climate
- 步骤数: 6
- 共用场景数: 1

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 粗细分辨率资料及任务边界预检
- desc: 界定“复杂地形区域100米风场同期空间降尺度”的任务范围并执行“粗细分辨率资料及任务边界预检”，核验粗网格风场、地形、陆海掩膜和辅助大气量的来源、覆盖、有效时间和可用边界。
- depend: []
- prompt: 面向“复杂地形区域100米风场同期空间降尺度”，读取{COARSE_INPUT}、{FINE_REFERENCE}、{TARGET_GRID}、{ANALYSIS_PERIOD}、{DATA_CUTOFF_TIME}并完成粗细分辨率资料及任务边界预检。逐项列出数据路径、版本、区域、时段、变量、单位、缺测和资料截止时间；任何必需资料不存在、晚于截止时间或与任务边界冲突时停止并标记BLOCKED。
- step_input:
  - {COARSE_INPUT} (required=True, type=str, var_name=粗分辨率输入, hint=输入粗分辨率资料路径。, default=None)
  - {FINE_REFERENCE} (required=True, type=str, var_name=高分辨率参考, hint=输入高分辨率参考路径。, default=None)
  - {TARGET_GRID} (required=True, type=str, var_name=目标网格, hint=输入目标网格规格。, default=None)
  - {ANALYSIS_PERIOD} (required=True, type=str, var_name=处理时段, hint=输入处理起止时间。, default=None)
  - {DATA_CUTOFF_TIME} (required=True, type=str, var_name=资料截止时间, hint=输入资料截止时间。, default=None)
- outputs: ['输入数据与版本清单', '任务范围和资料截止时间表', '输入完整性预检报告']
- quality_gate: ['所有必需输入均存在且路径、版本和来源可追溯', '任务区域、时段、变量和输出目标无歧义', '缺测、重复和异常资料已记录且未擅自补造', '粗细分辨率样本严格同期且坐标一致']

### s02 粗细分辨率资料时空对齐与样本构造
- desc: 执行“粗细分辨率资料时空对齐与样本构造”，统一粗网格风场、地形、陆海掩膜和辅助大气量的时间、空间、单位、质量标志和缺测处理，形成可复现输入。
- depend: ['s01']
- prompt: 依据{PAIRING_CONFIG}、{SPLIT_PROTOCOL}、{PREPROCESS_CONFIG}完成粗细分辨率资料时空对齐与样本构造。对所有资料执行时空对齐、单位转换、掩膜和缺测处理，记录每一项转换前后形状、范围与时间轴；不得用验证期或目标时刻之后的信息补齐输入。
- step_input:
  - {PAIRING_CONFIG} (required=True, type=str, var_name=样本配对配置, hint=输入粗细样本配对配置。, default=None)
  - {SPLIT_PROTOCOL} (required=True, type=str, var_name=数据划分协议, hint=输入数据划分协议。, default=None)
  - {PREPROCESS_CONFIG} (required=True, type=str, var_name=预处理配置, hint=输入预处理配置。, default=None)
- outputs: ['对齐后的标准输入', '掩膜与样本索引', '预处理转换记录']
- quality_gate: ['预处理后的时间轴、坐标、单位和形状可检查', '每项插值、归一化、掩膜和缺测处理均有记录', '不存在由验证资料或未来资料造成的信息泄漏', '训练与验证时空块互斥并防止目标泄漏']

### s03 方法配置与输入输出契约验证
- desc: 执行“方法配置与输入输出契约验证”，冻结方法工件、参数和随机性配置，并以小样本检查输入输出契约。
- depend: ['s02']
- prompt: 依据{METHOD_ARTIFACT}、{METHOD_CONFIG}、{RANDOM_SEED}加载方法工件与配置并完成方法配置与输入输出契约验证。核对变量顺序、张量或表结构、目标定义和输出契约，执行最小干运行；版本不匹配、出现缺失字段或异常数值时停止并标记BLOCKED。
- step_input:
  - {METHOD_ARTIFACT} (required=True, type=str, var_name=方法工件, hint=输入方法工件路径。, default=None)
  - {METHOD_CONFIG} (required=True, type=str, var_name=方法配置, hint=输入方法参数配置。, default=None)
  - {RANDOM_SEED} (required=True, type=str, var_name=随机种子, hint=输入可复现实验种子。, default=0)
- outputs: ['方法工件与配置身份报告', '输入输出兼容性矩阵', '最小干运行日志']
- quality_gate: ['方法工件、配置和运行环境属于兼容版本', '目标变量和输出结构与任务定义一致', '最小干运行正常退出且结果不存在NaN或Inf', '训练与验证时空块互斥并防止目标泄漏']

### s04 重建细网格水平风矢量
- desc: 按冻结配置执行“重建细网格水平风矢量”，完成从粗网格风场、地形、陆海掩膜和辅助大气量到高分辨率100米风速与风向格点的核心计算并保存逐阶段日志。
- depend: ['s03']
- prompt: 依据{RUN_CONFIG}、{ENSEMBLE_SIZE}、{OUTPUT_INTERVAL}执行重建细网格水平风矢量，将粗网格风场、地形、陆海掩膜和辅助大气量转换为高分辨率100米风速与风向格点。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。
- step_input:
  - {RUN_CONFIG} (required=True, type=str, var_name=运行配置, hint=输入运行参数配置。, default=None)
  - {ENSEMBLE_SIZE} (required=True, type=str, var_name=生成成员数, hint=输入生成成员数量。, default=1)
  - {OUTPUT_INTERVAL} (required=True, type=str, var_name=输出间隔, hint=输入结果输出间隔。, default=None)
- outputs: ['重建细网格水平风矢量结果', '中间状态与运行日志', '资源和退出状态记录']
- quality_gate: ['目标区域和时段内结果完整且无重复或错位', '核心计算未读取任务截止时间之后的数据', '配置、随机种子、日志和中间状态能够追溯', '输出均值、极端尾部和空间频谱均可检查']

### s05 结果恢复与场景产品生成
- desc: 执行“结果恢复与场景产品生成”，恢复物理量、坐标和元数据，生成高分辨率100米风速与风向格点及必要的质量标志。
- depend: ['s04']
- prompt: 依据{OUTPUT_FORMAT}、{OUTPUT_DIRECTORY}、{POSTPROCESS_CONFIG}、{DERIVED_PRODUCTS}完成结果恢复与场景产品生成，对核心结果执行已登记的校准、订正、派生或聚合并输出高分辨率100米风速与风向格点。核验单位、坐标、时次、无效值、物理范围和文件可读性；派生量必须记录公式和源变量。
- step_input:
  - {OUTPUT_FORMAT} (required=True, type=str, var_name=输出格式, hint=输入输出文件格式。, default=None)
  - {OUTPUT_DIRECTORY} (required=True, type=str, var_name=结果保存路径, hint=输入结果保存路径。, default=None)
  - {POSTPROCESS_CONFIG} (required=False, type=str, var_name=后处理配置, hint=输入订正派生聚合配置。, default=None)
  - {DERIVED_PRODUCTS} (required=False, type=str, var_name=派生产品, hint=输入派生产品清单。, default=None)
- outputs: ['高分辨率100米风速与风向格点', '质量标志与不确定性信息', '产品元数据与文件清单']
- quality_gate: ['输出文件能够重新打开且变量和元数据完整', '结果单位、坐标、有效时间和物理范围已核验', '派生产品均有明确公式、源变量和质量标志', '输出均值、极端尾部和空间频谱均可检查']

### s06 检验MAE及跨区域迁移误差
- desc: 执行“检验MAE及跨区域迁移误差”，使用未参与参数选择的参考资料检验高分辨率100米风速与风向格点，给出适用范围与交付判定。
- depend: ['s05']
- prompt: 依据{VERIFICATION_REFERENCE}、{BENCHMARK_RESULT}、{METRICS}、{ACCEPTANCE_CRITERIA}以独立参考资料完成检验MAE及跨区域迁移误差。按预先登记的区域、时段、事件或提前期计算指标并与同协议基线比较；缺少参考资料或验收门限时只能报告结果，不得声明性能PASS。
- step_input:
  - {VERIFICATION_REFERENCE} (required=True, type=str, var_name=独立验证资料, hint=输入独立验证资料路径。, default=None)
  - {BENCHMARK_RESULT} (required=False, type=str, var_name=基线结果, hint=输入同协议基线结果。, default=None)
  - {METRICS} (required=True, type=str, var_name=检验指标, hint=输入检验指标，逗号分隔。, default=None)
  - {ACCEPTANCE_CRITERIA} (required=False, type=str, var_name=验收门限, hint=输入预先登记的门限。, default=None)
- outputs: ['分层检验指标报告', '同协议基线比较报告', '适用边界与交付判定']
- quality_gate: ['验证资料未参与训练、参数选择或阈值调优', '结果与基线采用相同样本、网格和指标协议', '未达到预先登记门限时不得判定性能通过', '配置、日志、产物路径和文件哈希可追溯', '与插值及同协议统计基线比较']

## 使用本工作流的场景（场景→工作流映射）
- E89
