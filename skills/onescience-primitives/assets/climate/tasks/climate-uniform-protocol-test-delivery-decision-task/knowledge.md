# 骨架任务：同协议检验与交付判定

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 验证资料可用时按变量、层次、区域和时效计算确定性技巧，并与同条件基线比较。

## 执行 prompt（跨场景聚合去重）
- 若{VERIFICATION_REFERENCE}可用，依据{VALIDATION_PROTOCOL}计算{METRICS}，并在同起报、同参考和同网格条件下比较{BENCHMARK_FORECAST}；同时检查频谱、预报活动度、异常极值和长滚动稳定性。资料或门限缺失时不得用论文结果替代本次验证。

## 输入槽（var/hint/default）
- {VERIFICATION_REFERENCE} | required=False | type=str | var_name=独立验证资料 | hint=输入验证资料路径。 | default=None
- {BENCHMARK_FORECAST} | required=False | type=str | var_name=基线预报 | hint=输入基线预报路径。 | default=None
- {METRICS} | required=True | type=str | var_name=检验指标 | hint=输入检验指标，逗号分隔。 | default=None
- {VALIDATION_PROTOCOL} | required=False | type=str | var_name=验证与验收协议 | hint=输入验收协议路径。 | default=None

## 产出
- 分变量分层分区域分时效技能报告
- 同协议基线比较报告
- 质量判定与交付清单
- 频谱、活动度与稳定性诊断

## 质量门禁 quality_gate
- 只有达到预先登记的验收门限才能判定性能PASS
- 指标按变量、层次、区域和时效分层报告
- 配置、命令、退出码、日志、产物路径和文件哈希可追溯
- 预报、基线和参考资料采用一致的起报时间、网格和面积权重
- 验证资料或门限缺失时不作性能通过声明
- 验证资料未参与本次模型输入或参数选择

## 可调资源（edge:resource，仅真实存在）
- datasets/kling-gupta-efficiency-kge-metric
- datasets/lpma-airport-wind-observation-validation
- datasets/mdn-based-chla-retrieval-benchmark
- datasets/precipitation-nowcasting-evaluation-metrics
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/wenhai-global-ocean-forecast-system

## 实例任务（本骨架在各场景的实例化）
- climate-uniform-protocol-test-global-analysis-driven-1-10-inst

## 复用场景
- E1
