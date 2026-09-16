# 实例任务：生成连续高分辨率场 @ E16

- domain: climate
- 骨架: climate-generate-continuous-high-resolution-field-task
- 场景: climate-remote-sensing-soil-moisture-kilometer-scale-spatial-scenario (E16)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E16
- 关联论文: Global downscaling of remotely sensed soil moisture using neural networks | doi:; Global long term daily 1 km surface soil moisture dataset with physics informed machine learning | doi:; Global soil moisture data derived through machine learning trained with in-situ measurements | doi:

## 本实例步骤描述
按冻结配置执行“生成连续高分辨率场”，完成从卫星土壤湿度、植被地表温度、地形土壤属性到高分辨率土壤湿度与质量标志的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{DOWNSCALING_CONFIG}、{TEMPORAL_FILL_POLICY}、{UNCERTAINTY_CONFIG}执行生成连续高分辨率场，将卫星土壤湿度、植被地表温度、地形土壤属性转换为高分辨率土壤湿度与质量标志。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {DOWNSCALING_CONFIG} | required=True | type=str | var_name=降尺度配置 | hint=输入降尺度运行配置。 | default=None
- {TEMPORAL_FILL_POLICY} | required=True | type=str | var_name=时序重建规则 | hint=输入时序重建规则。 | default=None
- {UNCERTAINTY_CONFIG} | required=False | type=str | var_name=不确定性配置 | hint=输入不确定性估计配置。 | default=None

## 本实例产出
- 生成连续高分辨率场结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 水量、状态范围和洪峰时序不存在非物理异常
- 空间降尺度与时间缺口重建结果可分别追溯

## 可调资源（edge:resource，仅真实存在）
- models/customized-deep-learning-for-precipitation-bias-correction-and-downscaling
- models/glm-downscaling-methods
- models/neural-network-soil-moisture-downscaling
- models/spatial-and-temporal-deep-learning-models-for-fire-prediction
- tools/cnn1-and-cnn10-models-for-downscaling

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
