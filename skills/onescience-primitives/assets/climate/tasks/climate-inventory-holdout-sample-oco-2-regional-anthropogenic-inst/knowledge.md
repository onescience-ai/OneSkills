# 实例任务：与清单及留区样本比较总量和格局 @ E84

- domain: climate
- 骨架: climate-inventory-holdout-sample-total-pattern-comparison-task
- 场景: climate-oco-2-regional-anthropogenic-co2-emission-inversion-scenario (E84)
- step_id: s06
- depend: ['s05']

## 场景研究主体
- E84
- 关联论文: Neural-network-based estimation of regional-scale anthropogenic CO 2 emissions using an Orbiting Carbon Observatory-2 (OCO-2) dataset over East and West Asia | doi:

## 本实例步骤描述
执行“与清单及留区样本比较总量和格局”，使用未参与参数选择的参考资料检验区域人为CO2排放量及空间分布，给出适用范围与交付判定。

## 本实例执行 prompt
依据{VERIFICATION_REFERENCE}、{BENCHMARK_RESULT}、{METRICS}、{ACCEPTANCE_CRITERIA}以独立参考资料完成与清单及留区样本比较总量和格局。按预先登记的区域、时段、事件或提前期计算指标并与同协议基线比较；缺少参考资料或验收门限时只能报告结果，不得声明性能PASS。

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
- 验证采用独立地点、日期或传感器资料

## 可调资源（edge:resource，仅真实存在）
- datasets/kling-gupta-efficiency-kge-metric
- datasets/mdn-based-chla-retrieval-benchmark
- datasets/precipitation-nowcasting-evaluation-metrics

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
