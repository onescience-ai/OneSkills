# 工作流：climate-forecast-range-and-radar-sequence-precheck-radar-quality-workflow

- domain: climate
- 步骤数: 6
- 共用场景数: 1

## 步骤序列（含依赖/输入槽/产出/质量门禁）
### s01 起报范围与雷达序列预检
- desc: 固定起报时间和预报时效，核验连续雷达历史序列的时间间隔、覆盖范围、变量、单位、缺测与资料截止时间。
- depend: []
- prompt: 读取{RADAR_HISTORY}，以{FORECAST_START_TIME}为起报时间，检查{HISTORY_FRAMES}帧、{FRAME_INTERVAL_MINUTES}分钟间隔和{DATA_CUTOFF_TIME}，并确认{FORECAST_HORIZON_MINUTES}不超过180分钟。报告覆盖、单位、缺帧、异常值和时间连续性；存在未来观测泄漏或关键帧缺失时停止并标记BLOCKED。
- step_input:
  - {RADAR_HISTORY} (required=True, type=str, var_name=连续雷达历史序列, hint=输入连续雷达数据路径。, default=None)
  - {FORECAST_START_TIME} (required=True, type=str, var_name=起报时间, hint=输入UTC起报时间。, default=None)
  - {HISTORY_FRAMES} (required=True, type=str, var_name=历史帧数, hint=输入连续历史雷达帧数。, default=9)
  - {FRAME_INTERVAL_MINUTES} (required=True, type=str, var_name=雷达帧间隔, hint=输入帧间隔，单位分钟。, default=10)
  - {FORECAST_HORIZON_MINUTES} (required=True, type=str, var_name=预报时长, hint=输入预报时长，不超过180分钟。, default=180)
  - {DATA_CUTOFF_TIME} (required=True, type=str, var_name=资料截止时间, hint=输入资料截止时间。, default=None)
- outputs: ['雷达输入文件与资料截止时间清单', '历史帧时间轴与覆盖报告', '雷达序列预检报告']
- quality_gate: ['所有输入雷达帧的有效时间均不晚于起报时间', '历史帧数量和时间间隔满足模型契约', '雷达变量、单位、投影和覆盖范围均可识别', '缺帧、缺测区和异常回波已显式记录']

### s02 雷达质控与模型输入构造
- desc: 执行缺测掩膜、异常值处理、网格统一、雨强变换和历史序列堆叠，形成模型输入。
- depend: ['s01']
- prompt: 依据{PREPROCESS_CONFIG}和{RADAR_GRID_SPEC}处理通过预检的雷达序列，应用{MISSING_VALUE_POLICY}，统一投影、网格、单位和值域，生成按时间堆叠的输入张量和有效区掩膜。不得将缺测编码为零降水。
- step_input:
  - {PREPROCESS_CONFIG} (required=True, type=str, var_name=雷达预处理配置, hint=输入预处理配置路径。, default=None)
  - {RADAR_GRID_SPEC} (required=True, type=str, var_name=雷达网格规格, hint=输入投影、分辨率和网格范围。, default=None)
  - {MISSING_VALUE_POLICY} (required=True, type=str, var_name=缺测处理策略, hint=输入掩膜或拒绝策略。, default=None)
- outputs: ['标准化雷达历史张量', '有效区与缺测掩膜', '雷达预处理转换清单']
- quality_gate: ['时间维、空间维、投影、单位和通道顺序与模型输入契约一致', '缺测区与无降水区能够区分', '裁剪和重采样没有引入时间错位', '输入张量不存在未解释的NaN、Inf或异常负值']

### s03 预测组件与参数兼容性验证
- desc: 加载所选预测组件的配置和参数文件，核验输入输出尺寸及成员采样接口并执行单次干运行。
- depend: ['s01']
- prompt: 加载{MODEL_CONFIG}和{MODEL_CHECKPOINT}，核对{CHECKPOINT_SHA256}，使用{RANDOM_SEED}执行单次成员干运行，并确认能够生成{ENSEMBLE_SIZE}个独立成员。报告代码、依赖、配置和权重版本；存在输入输出不兼容或随机接口失效时停止。
- step_input:
  - {MODEL_CHECKPOINT} (required=True, type=str, var_name=预测组件参数路径, hint=输入模型权重文件路径。, default=None)
  - {MODEL_CONFIG} (required=True, type=str, var_name=预测组件配置路径, hint=输入模型配置文件路径。, default=None)
  - {CHECKPOINT_SHA256} (required=False, type=str, var_name=权重SHA-256, hint=输入权重SHA-256。, default=None)
  - {ENSEMBLE_SIZE} (required=True, type=str, var_name=集合成员数, hint=输入集合成员数量。, default=20)
  - {RANDOM_SEED} (required=False, type=str, var_name=随机种子, hint=输入随机种子。, default=None)
- outputs: ['模型与检查点身份报告', '输入输出兼容性矩阵', '单成员干运行日志', '集合采样配置']
- quality_gate: ['检查点SHA-256与登记值一致', '代码、配置、预处理参数和检查点属于兼容版本', '单成员输出时空尺寸和值域正确', '固定随机种子时结果可复现，不同成员具有可辨别差异', '集合规模对应的推理和存储资源已核算']

### s04 0—3小时集合降水生成
- desc: 使用已验证的时空预测组件和成员生成配置，生成未来多时次高分辨率降水率集合。
- depend: ['s02', 's03']
- prompt: 使用已验证的模型、雷达张量和集合配置，按{OUTPUT_INTERVAL_MINUTES}分钟间隔生成至{FORECAST_HORIZON_MINUTES}分钟的降水率集合。根据{SAVE_MEMBER_FIELDS}保存成员格点场，逐成员记录随机种子、输出值域、耗时和异常状态。
- step_input:
  - {OUTPUT_INTERVAL_MINUTES} (required=True, type=str, var_name=输出时间间隔, hint=输入输出间隔，单位分钟。, default=10)
  - {SAVE_MEMBER_FIELDS} (required=True, type=str, var_name=保存成员格点场, hint=输入是否保存成员场。, default=true)
- outputs: ['多成员降水率预报序列', '集合均值与分位数场', '逐成员推理日志与资源统计']
- quality_gate: ['预报时次完整且不超过180分钟', '所有成员的空间网格、时间轴和单位一致', '输出不存在未解释的NaN、Inf或负雨强', '成员差异来自登记的随机采样而非版本或输入不一致', '推理过程中未读取起报时间之后的雷达观测']

### s05 概率校准与短临产品生成
- desc: 计算雨强超阈概率和集合统计，并在独立校准资料可用时执行概率校准。
- depend: ['s04']
- prompt: 依据{RAIN_RATE_THRESHOLDS}计算各时效的超阈概率、集合均值和分位数。若{CALIBRATION_MODE}为independent_validation_calibration，必须使用{CALIBRATION_REFERENCE}拟合并记录校准映射；否则把产品明确标记为未校准。按{OUTPUT_FORMAT}写入{OUTPUT_DIRECTORY}并保存完整元数据。
- step_input:
  - {CALIBRATION_REFERENCE} (required=False, type=str, var_name=独立校准资料, hint=输入校准资料路径。, default=None)
  - {CALIBRATION_MODE} (required=True, type=str, var_name=概率校准模式, hint=输入校准方式或不校准。, default=None)
  - {RAIN_RATE_THRESHOLDS} (required=True, type=str, var_name=雨强阈值, hint=输入雨强阈值，逗号分隔。, default=None)
  - {OUTPUT_FORMAT} (required=True, type=str, var_name=输出格式, hint=输入NetCDF或Zarr。, default=None)
  - {OUTPUT_DIRECTORY} (required=True, type=str, var_name=结果保存路径, hint=输入预报结果保存路径。, default=None)
- outputs: ['降水率集合成员或集合统计', '逐阈值逐时效超阈概率', '概率校准记录或未校准标识', '产品元数据与文件清单']
- quality_gate: ['概率值位于0到1且随阈值变化不存在逻辑矛盾', '校准资料与训练及最终测试资料相互独立', '没有校准证据时未将原始生成集合声称为已校准概率预报', '输出文件能够重新打开且坐标、单位、时效和成员维完整', '模型、检查点、随机种子和校准版本可追溯']

### s06 分时效多阈值检验与交付判定
- desc: 未来雷达资料可用时，对位置、结构、极端雨强和概率可靠性开展分时效验证。
- depend: ['s05']
- prompt: 若{VERIFICATION_RADAR}可用，依据{VALIDATION_PROTOCOL}计算{METRICS}，并与相同起报时间和输入截止时间的{BASELINE_NOWCASTS}比较。分别报告普通样本、强降水样本和不同提前量，不得把重要性抽样结果外推为全年总体表现。资料或门限缺失时不得判定性能PASS。
- step_input:
  - {VERIFICATION_RADAR} (required=False, type=str, var_name=未来验证雷达资料, hint=输入未来雷达资料路径。, default=None)
  - {BASELINE_NOWCASTS} (required=False, type=str, var_name=基线临近预报, hint=输入基线预报路径。, default=None)
  - {METRICS} (required=True, type=str, var_name=检验指标, hint=输入检验指标，逗号分隔。, default=None)
  - {VALIDATION_PROTOCOL} (required=False, type=str, var_name=验证与验收协议, hint=输入验收协议路径。, default=None)
- outputs: ['分时效分阈值分尺度技能报告', '概率可靠性与集合离散度报告', '同协议基线比较报告', '强降水与普通样本分层结果', '质量判定与交付清单']
- quality_gate: ['预报、基线和验证雷达采用一致的网格、掩膜、单位和有效时刻', '验证资料未参与模型输入、训练或概率校准', '确定性、空间结构和概率指标均按提前量分层报告', '重要性抽样与连续时段验证结果分别报告', '只有达到预先登记的验收门限才能判定性能PASS', '验证资料或门限缺失时不作性能通过声明', '配置、命令、退出码、日志、产物路径和文件哈希可追溯']

## 使用本工作流的场景（场景→工作流映射）
- E2
