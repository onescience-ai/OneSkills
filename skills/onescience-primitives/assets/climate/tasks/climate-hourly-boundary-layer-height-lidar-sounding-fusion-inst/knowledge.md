# 实例任务：估计逐时边界层高度 @ E61

- domain: climate
- 骨架: climate-hourly-boundary-layer-height-estimation-task
- 场景: climate-lidar-sounding-fusion-boundary-layer-height-retrieval-scenario (E61)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E61
- 关联论文: On the estimation of boundary layer heights- a machine learning approach | doi:; Deriving boundary layer height from aerosol lidar using machine learning- KABL and ADABL algorithms | doi:

## 本实例步骤描述
按冻结配置执行“估计逐时边界层高度”，完成从激光雷达后向散射剖面、探空、地面气象到边界层高度时间序列和置信度的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{OUTPUT_RESOLUTION}、{DECISION_THRESHOLD}执行估计逐时边界层高度，将激光雷达后向散射剖面、探空、地面气象转换为边界层高度时间序列和置信度。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {OUTPUT_RESOLUTION} | required=True | type=str | var_name=输出分辨率 | hint=输入输出分辨率。 | default=None
- {DECISION_THRESHOLD} | required=False | type=str | var_name=诊断阈值 | hint=输入诊断判定阈值。 | default=None

## 本实例产出
- 估计逐时边界层高度结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 参考定义或标签未泄漏到待诊断样本

## 可调资源（edge:resource，仅真实存在）
- models/ensemble-model-output-statistics-emos-post-processing
- tools/ecmwf-hres

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
