# 实例任务：检验CRPS、覆盖率和可靠度 @ E14

- domain: climate
- 骨架: climate-crps-coverage-reliability-task
- 场景: climate-station-temperature-ensemble-forecast-probability-calibration-scenario (E14)
- step_id: s06
- depend: ['s05']

## 场景研究主体
- E14
- 关联论文: Neural Networks for Postprocessing Ensemble Weather Forecasts | doi:; From research to applications – examples of operational ensemble post-processing in France using machine learning | doi:; A Composite-Loss Graph Neural Network for the Multivariate Post-Processing of Ensemble Weather Forecasts | doi:; Ensemble weather forecast post-processing with a flexible probabilistic neural network approach | doi:

## 本实例步骤描述
执行“检验CRPS、覆盖率和可靠度”，使用未参与参数选择的参考资料检验温度分布参数、分位数和预测区间，给出适用范围与交付判定。

## 本实例执行 prompt
依据{VERIFICATION_REFERENCE}、{BENCHMARK_RESULT}、{METRICS}、{ACCEPTANCE_CRITERIA}以独立参考资料完成检验CRPS、覆盖率和可靠度。按预先登记的区域、时段、事件或提前期计算指标并与同协议基线比较；缺少参考资料或验收门限时只能报告结果，不得声明性能PASS。

## 本实例输入槽
- {VERIFICATION_REFERENCE} | required=True | type=str | var_name=独立验证资料 | hint=输入独立验证资料路径。 | default=None
- {BENCHMARK_RESULT} | required=False | type=str | var_name=基线结果 | hint=输入同协议基线结果。 | default=None
- {METRICS} | required=True | type=str | var_name=检验指标 | hint=输入检验指标，逗号分隔。 | default=None
- {ACCEPTANCE_CRITERIA} | required=False | type=str | var_name=验收门限 | hint=输入预先登记的门限。 | default=None

## 本实例产出
- 分层检验指标报告
- 同协议基线比较报告
- 适用边界与交付判定

## 本实例质量门禁
- 验证资料未参与训练、参数选择或阈值调优
- 结果与基线采用相同样本、网格和指标协议
- 未达到预先登记门限时不得判定性能通过
- 配置、日志、产物路径和文件哈希可追溯
- 技巧、可靠度、分辨率和锐度与原始预报同协议比较
- CRPS、覆盖率、可靠度和锐度均与原集合比较

## 可调资源（edge:resource，仅真实存在）
- datasets/kling-gupta-efficiency-kge-metric
- datasets/mdn-based-chla-retrieval-benchmark
- datasets/precipitation-nowcasting-evaluation-metrics

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
