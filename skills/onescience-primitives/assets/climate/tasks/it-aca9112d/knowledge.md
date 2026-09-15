# 实例任务：逐3小时预测区域浓度场 @ E99

- domain: climate
- 骨架: tk-climate-afebf2cb
- 场景: sc-2eb9b3c3 (E99)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E99
- 关联论文: Regional aerosol forecasts based on deep learning and numerical weather prediction | doi:

## 本实例步骤描述
按冻结配置执行“逐3小时预测区域浓度场”，完成从污染站历史、NWP气象场、排放清单到分时效PM2.5或气溶胶浓度格点与高污染区域的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{FORECAST_HORIZON}、{SPATIAL_GRID}执行逐3小时预测区域浓度场，将污染站历史、NWP气象场、排放清单转换为分时效PM2.5或气溶胶浓度格点与高污染区域。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {FORECAST_HORIZON} | required=False | type=str | var_name=预测时效 | hint=输入目标预测时效。 | default=None
- {SPATIAL_GRID} | required=True | type=str | var_name=输出网格 | hint=输入输出网格规格。 | default=None

## 本实例产出
- 逐3小时预测区域浓度场结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 输出浓度或柱含量满足物理范围和掩膜约束

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
