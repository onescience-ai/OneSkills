# 实例任务：模型与检查点兼容性验证 @ E1

- domain: climate
- 骨架: climate-model-checkpoint-compatibility-verification-task
- 场景: climate-global-analysis-driven-1-10-day-multivariate-deterministic-scenario (E1)
- step_id: s03
- depend: ['s01']

## 场景研究主体
- E1
- 关联论文: Learning skillful medium-range global weather forecasting | doi:; Accurate medium-range global weather forecasting with 3D neural networks | doi:; FourCastNet: A Global Data-driven High-resolution Weather Model using Adaptive Fourier Neural Operators | doi:; FengWu: Pushing the Skillful Global Medium-range Weather Forecast beyond 10 Days Lead | doi:; AIFS -- ECMWF's data-driven forecasting system | doi:

## 本实例步骤描述
加载模型代码、配置和检查点，核验版本、哈希、输入输出通道并执行单步干运行。

## 本实例执行 prompt
加载{MODEL_CONFIG}和{MODEL_CHECKPOINT}，核对{CHECKPOINT_SHA256}，在{RUNTIME_DEVICE}上执行一个原生时间步的干运行。报告代码、依赖、配置和权重版本；存在通道错配、缺失权重或未登记转换时停止。

## 本实例输入槽
- {MODEL_CHECKPOINT} | required=True | type=str | var_name=模型权重路径 | hint=输入模型权重文件路径。 | default=None
- {MODEL_CONFIG} | required=True | type=str | var_name=模型配置路径 | hint=输入模型配置文件路径。 | default=None
- {CHECKPOINT_SHA256} | required=False | type=str | var_name=权重SHA-256 | hint=输入权重SHA-256。 | default=None
- {RUNTIME_DEVICE} | required=True | type=str | var_name=推理设备 | hint=输入运行设备，如GPU。 | default=None

## 本实例产出
- 模型与检查点身份报告
- 输入输出兼容性矩阵
- 单步干运行日志

## 本实例质量门禁
- 检查点SHA-256与登记值一致
- 代码、配置、标准化参数和检查点属于兼容版本
- 不存在缺失或意外的权重、变量和通道
- 单步干运行正常退出且输出形状和值域可检查

## 可调资源（edge:resource，仅真实存在）
- datasets/forecasting-model-performance-evaluation
- datasets/random-forest-model-performance-evaluation
- models/dynamic-pre-training-for-time-series-dynpt
- models/ensemble-empirical-mode-decomposition-eemd
- models/ensemble-model-output-statistics-emos-post-processing
- models/neural-network-based-nwp-model-calibration
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
