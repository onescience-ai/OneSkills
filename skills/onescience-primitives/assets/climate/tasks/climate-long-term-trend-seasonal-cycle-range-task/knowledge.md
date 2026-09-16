# 骨架任务：检查长期趋势、季节循环和物理范围

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 执行“检查长期趋势、季节循环和物理范围”，使用未参与参数选择的参考资料检验0.05°历史及情景LAI序列，给出适用范围与交付判定。

## 执行 prompt（跨场景聚合去重）
- 依据{VERIFICATION_REFERENCE}、{BENCHMARK_RESULT}、{METRICS}、{ACCEPTANCE_CRITERIA}以独立参考资料完成检查长期趋势、季节循环和物理范围。按预先登记的区域、时段、事件或提前期计算指标并与同协议基线比较；缺少参考资料或验收门限时只能报告结果，不得声明性能PASS。

## 输入槽（var/hint/default）
- {VERIFICATION_REFERENCE} | required=True | type=str | var_name=独立验证资料 | hint=输入独立验证资料路径。 | default=None
- {BENCHMARK_RESULT} | required=False | type=str | var_name=基线结果 | hint=输入同协议基线结果。 | default=None
- {METRICS} | required=True | type=str | var_name=检验指标 | hint=输入检验指标，逗号分隔。 | default=None
- {ACCEPTANCE_CRITERIA} | required=False | type=str | var_name=验收门限 | hint=输入预先登记的门限。 | default=None

## 产出
- 分层检验指标报告
- 同协议基线比较报告
- 适用边界与交付判定

## 质量门禁 quality_gate
- 与插值及同协议统计基线比较
- 未达到预先登记门限时不得判定性能通过
- 结果与基线采用相同样本、网格和指标协议
- 配置、日志、产物路径和文件哈希可追溯
- 验证资料未参与训练、参数选择或阈值调优

## 可调资源（edge:resource，仅真实存在）
- datasets/kling-gupta-efficiency-kge-metric
- datasets/mdn-based-chla-retrieval-benchmark
- datasets/precipitation-nowcasting-evaluation-metrics

## 实例任务（本骨架在各场景的实例化）
- climate-long-term-trend-seasonal-china-0-05-historical-inst

## 复用场景
- E93
