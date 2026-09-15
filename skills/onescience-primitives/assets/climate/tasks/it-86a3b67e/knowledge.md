# 实例任务：验证CRPS覆盖率和可靠度 @ E24

- domain: climate
- 骨架: tk-climate-4d09df02
- 场景: sc-fe3c0d54 (E24)
- step_id: s06
- depend: ['s05']

## 场景研究主体
- E24
- 关联论文: Improving Model Chain Approaches for Probabilistic Solar Energy Forecasting through Post-processing and Machine Learning | doi:; Post-processing numerical weather prediction ensembles for probabilistic solar irradiance forecasting | doi:; Comparison of statistical post-processing methods for probabilistic NWP forecasts of solar radiation | doi:; Machine-learning-based probabilistic forecasting of solar irradiance in Chile | doi:

## 本实例步骤描述
执行“验证CRPS覆盖率和可靠度”，使用未参与参数选择的参考资料检验校准辐照度分布、分位数和区间，给出适用范围与交付判定。

## 本实例执行 prompt
依据{VERIFICATION_REFERENCE}、{BENCHMARK_RESULT}、{METRICS}、{ACCEPTANCE_CRITERIA}以独立参考资料完成验证CRPS覆盖率和可靠度。按预先登记的区域、时段、事件或提前期计算指标并与同协议基线比较；缺少参考资料或验收门限时只能报告结果，不得声明性能PASS。

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
- 按站点、天气型和提前期检验校准度与锐度

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
