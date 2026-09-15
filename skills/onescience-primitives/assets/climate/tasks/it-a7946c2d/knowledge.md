# 实例任务：按站点留一法验证 @ E26

- domain: climate
- 骨架: tk-climate-dd4f5814
- 场景: sc-2528a6c2 (E26)
- step_id: s06
- depend: ['s05']

## 场景研究主体
- E26
- 关联论文: A machine learning model for hub-height short-term wind speed prediction | doi:; Estimating hub-height wind speed based on a machine learning algorithm- implications for wind energy assessment | doi:; Terrain-aware Deep Learning for Wind Energy Applications- From Kilometer-scale Forecasts to Fine Wind Fields | doi:; The importance of round-robin validation when assessing machine-learning-based vertical extrapolation of wind speeds | doi:

## 本实例步骤描述
执行“按站点留一法验证”，使用未参与参数选择的参考资料检验轮毂高度风速风向及误差范围，给出适用范围与交付判定。

## 本实例执行 prompt
依据{VERIFICATION_REFERENCE}、{BENCHMARK_RESULT}、{METRICS}、{ACCEPTANCE_CRITERIA}以独立参考资料完成按站点留一法验证。按预先登记的区域、时段、事件或提前期计算指标并与同协议基线比较；缺少参考资料或验收门限时只能报告结果，不得声明性能PASS。

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
- 与持续性和业务基线按时效及场站检验
- 按风场、地形分区和站点留一法分别检验

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
