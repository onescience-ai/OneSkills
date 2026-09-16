# 实例任务：将指纹投影到多套观测产品 @ E94

- domain: climate
- 骨架: climate-fingerprint-projection-multiple-observation-products-task
- 场景: climate-daily-precipitation-field-anthropogenic-climate-change-scenario (E94)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E94
- 关联论文: Anthropogenic fingerprints in daily precipitation revealed by deep learning | doi:

## 本实例步骤描述
按冻结配置执行“将指纹投影到多套观测产品”，完成从气候模式大集合日降水、观测日降水到人为指纹得分、空间贡献和检测时间序列的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{FINGERPRINT_CONFIG}、{RESAMPLING_COUNT}、{SIGNIFICANCE_LEVEL}执行将指纹投影到多套观测产品，将气候模式大集合日降水、观测日降水转换为人为指纹得分、空间贡献和检测时间序列。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {FINGERPRINT_CONFIG} | required=True | type=str | var_name=指纹投影配置 | hint=输入指纹投影配置。 | default=None
- {RESAMPLING_COUNT} | required=True | type=str | var_name=重采样次数 | hint=输入重采样次数。 | default=1000
- {SIGNIFICANCE_LEVEL} | required=True | type=str | var_name=显著性水平 | hint=输入显著性水平。 | default=0.05

## 本实例产出
- 将指纹投影到多套观测产品结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 检测、关联和因果归因结论被明确区分
- 冻结训练得到的指纹后才投影到独立观测产品

## 可调资源（edge:resource，仅真实存在）
- datasets/smap-level-3-passive-soil-moisture-products
- models/1d-cnn-based-groundwater-level-prediction
- models/importance-sampling-strategy-for-extreme-events
- tools/multi-level-b-spline-analysis-mba

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
