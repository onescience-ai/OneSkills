# 实例任务：逐时效预测位移或轨迹点 @ E30

- domain: climate
- 骨架: climate-predict-displacement-or-trajectory-by-lead-time-task
- 场景: climate-identified-tropical-cyclone-track-forecast-24-120h-scenario (E30)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E30
- 关联论文: Tropical Cyclone Track Forecasting Using Fused Deep Learning From Aligned Reanalysis Data | doi:; Dual-Branched Spatio-Temporal Fusion Network for Multihorizon Tropical Cyclone Track Forecast | doi:; Forecasting tropical cyclone tracks in the northwestern Pacific based on a deep-learning model | doi:

## 本实例步骤描述
按冻结配置执行“逐时效预测位移或轨迹点”，完成从气旋历史位置、强度元数据、风暴中心环境场到多时效中心经纬度、路径和登陆概率的核心计算并保存逐阶段日志。

## 本实例执行 prompt
依据{RUN_CONFIG}、{OUTPUT_INTERVAL}、{ENSEMBLE_SIZE}执行逐时效预测位移或轨迹点，将气旋历史位置、强度元数据、风暴中心环境场转换为多时效中心经纬度、路径和登陆概率。保存配置、随机种子、开始结束时间、退出状态和中间产物；不得临时更换数据、阈值或方法版本。

## 本实例输入槽
- {RUN_CONFIG} | required=True | type=str | var_name=运行配置 | hint=输入运行参数配置。 | default=None
- {OUTPUT_INTERVAL} | required=True | type=str | var_name=输出间隔 | hint=输入结果输出间隔。 | default=None
- {ENSEMBLE_SIZE} | required=True | type=str | var_name=集合成员数 | hint=输入集合成员数量。 | default=1

## 本实例产出
- 逐时效预测位移或轨迹点结果
- 中间状态与运行日志
- 资源和退出状态记录

## 本实例质量门禁
- 目标区域和时段内结果完整且无重复或错位
- 核心计算未读取任务截止时间之后的数据
- 配置、随机种子、日志和中间状态能够追溯
- 滚动过程中未读取起报时间之后的观测或分析资料

## 可调资源（edge:resource，仅真实存在）
- datasets/cesm2-large-ensemble
- datasets/large-ensemble-testbed
- models/crpsexp-loss-function-for-ensemble-forecasting
- models/ensemble-empirical-mode-decomposition-eemd
- models/ensemble-model-output-statistics-emos-post-processing

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
