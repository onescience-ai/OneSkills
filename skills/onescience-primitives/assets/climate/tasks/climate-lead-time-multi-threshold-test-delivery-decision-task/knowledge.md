# 骨架任务：分时效多阈值检验与交付判定

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 未来雷达资料可用时，对位置、结构、极端雨强和概率可靠性开展分时效验证。

## 执行 prompt（跨场景聚合去重）
- 若{VERIFICATION_RADAR}可用，依据{VALIDATION_PROTOCOL}计算{METRICS}，并与相同起报时间和输入截止时间的{BASELINE_NOWCASTS}比较。分别报告普通样本、强降水样本和不同提前量，不得把重要性抽样结果外推为全年总体表现。资料或门限缺失时不得判定性能PASS。

## 输入槽（var/hint/default）
- {VERIFICATION_RADAR} | required=False | type=str | var_name=未来验证雷达资料 | hint=输入未来雷达资料路径。 | default=None
- {BASELINE_NOWCASTS} | required=False | type=str | var_name=基线临近预报 | hint=输入基线预报路径。 | default=None
- {METRICS} | required=True | type=str | var_name=检验指标 | hint=输入检验指标，逗号分隔。 | default=None
- {VALIDATION_PROTOCOL} | required=False | type=str | var_name=验证与验收协议 | hint=输入验收协议路径。 | default=None

## 产出
- 分时效分阈值分尺度技能报告
- 同协议基线比较报告
- 强降水与普通样本分层结果
- 概率可靠性与集合离散度报告
- 质量判定与交付清单

## 质量门禁 quality_gate
- 只有达到预先登记的验收门限才能判定性能PASS
- 确定性、空间结构和概率指标均按提前量分层报告
- 配置、命令、退出码、日志、产物路径和文件哈希可追溯
- 重要性抽样与连续时段验证结果分别报告
- 预报、基线和验证雷达采用一致的网格、掩膜、单位和有效时刻
- 验证资料或门限缺失时不作性能通过声明
- 验证资料未参与模型输入、训练或概率校准

## 可调资源（edge:resource，仅真实存在）
- datasets/kling-gupta-efficiency-kge-metric
- datasets/lpma-airport-wind-observation-validation
- datasets/precipitation-nowcasting-evaluation-metrics
- datasets/uk-radar-composite-dataset
- tools/lhasa-v2-global-rainfall-triggered-landslide-probabilistic-nowcast-model

## 实例任务（本骨架在各场景的实例化）
- climate-lead-time-multi-threshold-radar-driven-0-3-hour-inst

## 复用场景
- E2
