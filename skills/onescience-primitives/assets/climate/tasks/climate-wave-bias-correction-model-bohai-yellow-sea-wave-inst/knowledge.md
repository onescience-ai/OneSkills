# 实例任务：海浪偏差订正模型训练与产品生成 @ E105

- domain: climate
- 骨架: climate-wave-bias-correction-model-product-task
- 场景: climate-bohai-yellow-sea-wave-intelligent-correction-scenario (E105)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E105
- 关联论文: A Deep Learning-Based Bias Correction Method for Predicting Ocean Surface Waves in the Northwest Pacific Ocean | doi:; WaveUformer: a bias correction model for GWSM4C Wave Forecasting | doi:; AI-based Correction of Wave Forecasts Using the Transformer-enhanced UNet Model | doi:

## 本实例步骤描述
学习业务海浪预报与观测参考之间的偏差，生成与原数值模式同契约的订正产品。

## 本实例执行 prompt
仅在s02任务配置冻结门禁和s03数据与干运行门禁均通过后执行；否则停止并标记BLOCKED。执行前核验本步骤全部输入值或路径已提供；对文件和数据类输入，核验其实际存在、可读、获准使用且与s03冻结的数据契约一致，并记录版本与校验信息；缺失或不一致时停止并标记BLOCKED。按s02冻结方案训练并冻结订正模型，对{TARGET_WAVE_FORECAST}中落在{TRIAL_PERIOD}内的全部冻结业务起报逐批运行，生成同变量、同网格、同时间分辨率的订正产品和偏差场至{OUTPUT_DIRECTORY}；保留逐批原始—订正对应、模型身份、缺报、失败、恢复和日志。

## 本实例输入槽
- {TARGET_WAVE_FORECAST} | required=True | type=str | var_name=待订正海浪产品 | hint=输入覆盖s02冻结试运行时段的待订正产品目录或清单。 | default=None
- {TRIAL_PERIOD} | required=True | type=str | var_name=试运行时段 | hint=输入连续试运行起止时间；时长须由s02冻结在1—2个月内。 | default=None
- {OUTPUT_DIRECTORY} | required=True | type=str | var_name=结果输出目录 | hint=输入产品输出目录。 | default=None

## 本实例产出
- 海浪智能订正模型与权重
- 连续试运行的订正海浪产品和偏差场
- 逐批原始—订正索引、缺报失败、恢复日志和产品清单

## 本实例质量门禁
- 训练目标和推理输入不存在未来观测泄漏
- 订正前后产品在变量、网格、时次、单位和方向约定上可对应
- 极端波浪样本未被静默剔除或平滑
- 模型、数据和训练配置可追溯
- 连续试运行覆盖s02冻结的1—2个月时段，全部业务起报均有产品或缺报、失败与恢复记录

## 可调资源（edge:resource，仅真实存在）
- models/ensemble-model-output-statistics-emos-post-processing
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/wenhai-global-ocean-forecast-system

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
