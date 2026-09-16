# 实例任务：用独立样地检验生物量并诊断气候响应 @ E96

- domain: climate
- 骨架: climate-validate-biomass-with-independent-plots-and-diagnose-climate-task
- 场景: climate-grassland-aboveground-biomass-remote-sensing-estimation-and-scenario (E96)
- step_id: s06
- depend: ['s05']

## 场景研究主体
- E96
- 关联论文: Machine learning-based grassland aboveground biomass estimation and its response to climate variation in Southwest China | doi:

## 本实例步骤描述
执行“用独立样地检验生物量并诊断气候响应”，使用未参与参数选择的参考资料检验草地地上生物量图及气候敏感性，给出适用范围与交付判定。

## 本实例执行 prompt
依据{INDEPENDENT_PLOT_DATA}、{CLIMATE_RESPONSE_VARIABLES}、{RESPONSE_DIAGNOSTICS}、{ACCEPTANCE_CRITERIA}以独立参考资料完成用独立样地检验生物量并诊断气候响应。按预先登记的区域、时段、事件或提前期计算指标并与同协议基线比较；缺少参考资料或验收门限时只能报告结果，不得声明性能PASS。

## 本实例输入槽
- {INDEPENDENT_PLOT_DATA} | required=True | type=str | var_name=独立样地资料 | hint=输入独立样地资料路径。 | default=None
- {CLIMATE_RESPONSE_VARIABLES} | required=True | type=str | var_name=气候响应变量 | hint=输入气候响应变量清单。 | default=None
- {RESPONSE_DIAGNOSTICS} | required=True | type=str | var_name=响应诊断配置 | hint=输入气候响应诊断配置。 | default=None
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
- 生物量估计误差与气候响应不确定性分别报告

## 可调资源（edge:resource，仅真实存在）
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/ostia-sst-data
- datasets/snodas-swe-data-product
- models/multivariate-data-fusion-vector-wind-prediction

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
