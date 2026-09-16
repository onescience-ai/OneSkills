# 实例任务：预测组件与参数兼容性验证 @ E2

- domain: climate
- 骨架: climate-predict-component-parameter-compatibility-verification-task
- 场景: climate-radar-driven-0-3-hour-extreme-precipitation-ensemble-nowcasting-scenario (E2)
- step_id: s03
- depend: ['s01']

## 场景研究主体
- E2
- 关联论文: Skilful nowcasting of extreme precipitation with NowcastNet | doi:; Skilful precipitation nowcasting using deep generative models of radar | doi:; Convolutional LSTM Network: A Machine Learning Approach for Precipitation Nowcasting | doi:; RainNet v1.0: a convolutional neural network for radar-based precipitation nowcasting | doi:

## 本实例步骤描述
加载所选预测组件的配置和参数文件，核验输入输出尺寸及成员采样接口并执行单次干运行。

## 本实例执行 prompt
加载{MODEL_CONFIG}和{MODEL_CHECKPOINT}，核对{CHECKPOINT_SHA256}，使用{RANDOM_SEED}执行单次成员干运行，并确认能够生成{ENSEMBLE_SIZE}个独立成员。报告代码、依赖、配置和权重版本；存在输入输出不兼容或随机接口失效时停止。

## 本实例输入槽
- {MODEL_CHECKPOINT} | required=True | type=str | var_name=预测组件参数路径 | hint=输入模型权重文件路径。 | default=None
- {MODEL_CONFIG} | required=True | type=str | var_name=预测组件配置路径 | hint=输入模型配置文件路径。 | default=None
- {CHECKPOINT_SHA256} | required=False | type=str | var_name=权重SHA-256 | hint=输入权重SHA-256。 | default=None
- {ENSEMBLE_SIZE} | required=True | type=str | var_name=集合成员数 | hint=输入集合成员数量。 | default=20
- {RANDOM_SEED} | required=False | type=str | var_name=随机种子 | hint=输入随机种子。 | default=None

## 本实例产出
- 模型与检查点身份报告
- 输入输出兼容性矩阵
- 单成员干运行日志
- 集合采样配置

## 本实例质量门禁
- 检查点SHA-256与登记值一致
- 代码、配置、预处理参数和检查点属于兼容版本
- 单成员输出时空尺寸和值域正确
- 固定随机种子时结果可复现，不同成员具有可辨别差异
- 集合规模对应的推理和存储资源已核算

## 可调资源（edge:resource，仅真实存在）
- datasets/cesm2-large-ensemble
- datasets/forecasting-model-performance-evaluation
- datasets/large-ensemble-testbed
- datasets/random-forest-model-performance-evaluation
- models/crpsexp-loss-function-for-ensemble-forecasting
- models/ensemble-empirical-mode-decomposition-eemd
- models/ensemble-model-output-statistics-emos-post-processing
- models/neural-network-based-nwp-model-calibration
- models/random-forest-meteorological-normalization
- models/random-forest-regression-for-vertical-wind-speed-extrapolation
- models/swe-reconstruction-using-energy-balance-model
- models/weighted-long-short-term-memory-neural-network-extended-model-for-pm2-5-forecasting
- tools/deep-learning-precipitation-retrieval-model-and-evaluation
- tools/gencast-global-probabilistic-weather-forecasting-model
- tools/lhasa-v2-global-rainfall-triggered-landslide-probabilistic-nowcast-model
- tools/multi-task-deep-learning-model-for-indian-ocean-dipole-prediction
- tools/parbal-energy-balance-model
- tools/urban-hydrological-hydraulic-model-chain-for-inundation-simulation

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
