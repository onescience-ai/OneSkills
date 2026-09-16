# 骨架任务：网格对齐与输入标准化

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 依据版本化模型输入契约执行重网格、变量排序、单位换算、标准化及静态地理特征编码。

## 执行 prompt（跨场景聚合去重）
- 根据{MODEL_INPUT_SPEC}和{PREPROCESS_CONFIG}处理通过预检的分析场，执行{MISSING_VALUE_POLICY}，生成与模型严格兼容的输入张量。记录每项重网格、单位换算、变量排序和标准化参数，保证处理可追溯。

## 输入槽（var/hint/default）
- {MODEL_INPUT_SPEC} | required=True | type=str | var_name=模型输入规格 | hint=输入模型类型，如Swin-transformer、GNN、AFNO。 | default=None
- {PREPROCESS_CONFIG} | required=True | type=str | var_name=预处理配置 | hint=输入预处理配置路径。 | default=None
- {MISSING_VALUE_POLICY} | required=True | type=str | var_name=缺测处理策略 | hint=输入拒绝或插补策略。 | default=None

## 产出
- 标准化模型输入张量
- 输入掩膜与静态特征
- 预处理转换清单

## 质量门禁 quality_gate
- 不存在模型不支持的NaN或Inf
- 张量维度、变量顺序、时次顺序和坐标方向与模型输入契约一致
- 归一化参数与检查点版本一致
- 经度周期、极点、日历和气压层顺序已核验

## 可调资源（edge:resource，仅真实存在）
- datasets/forecasting-model-performance-evaluation
- datasets/random-forest-model-performance-evaluation
- models/ensemble-empirical-mode-decomposition-eemd
- models/ensemble-model-output-statistics-emos-post-processing
- models/matern-gaussian-process-regression
- models/neural-network-based-nwp-model-calibration
- models/swe-reconstruction-using-energy-balance-model
- models/weighted-long-short-term-memory-neural-network-extended-model-for-pm2-5-forecasting
- tools/deep-learning-precipitation-retrieval-model-and-evaluation
- tools/gencast-global-probabilistic-weather-forecasting-model
- tools/lhasa-v2-global-rainfall-triggered-landslide-probabilistic-nowcast-model
- tools/multi-task-deep-learning-model-for-indian-ocean-dipole-prediction
- tools/parbal-energy-balance-model
- tools/urban-hydrological-hydraulic-model-chain-for-inundation-simulation

## 实例任务（本骨架在各场景的实例化）
- climate-grid-alignment-and-input-global-analysis-driven-1-10-inst

## 复用场景
- E1
