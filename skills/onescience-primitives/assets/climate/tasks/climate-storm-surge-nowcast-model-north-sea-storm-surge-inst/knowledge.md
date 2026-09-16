# 实例任务：风暴潮临近预报模型训练与实时产品生成 @ E101

- domain: climate
- 骨架: climate-storm-surge-nowcast-model-training-real-time-product-generation-task
- 场景: climate-north-sea-storm-surge-nowcast-model-scenario (E101)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E101
- 关联论文: 基于多变量LSTM神经网络模型的风暴潮临近预报 | doi:

## 本实例步骤描述
构建、训练并冻结临近预报模型，融合定时预报与实时逐小时潮位、气象资料，随时生成未来3天站点和空间产品。

## 本实例执行 prompt
仅在s02任务配置冻结门禁和s03数据与干运行门禁均通过后执行；否则停止并标记BLOCKED。执行前核验本步骤全部输入值或路径已提供；对文件和数据类输入，核验其实际存在、可读、获准使用且与s03冻结的数据契约一致，并记录版本与校验信息；缺失或不一致时停止并标记BLOCKED。按s02冻结方案构建并训练风暴潮临近预报模型，完成独立于验收集的调参与模型冻结，保留训练记录和权重；随后融合定时预报与实时资料，生成{FORECAST_HORIZON}、{OUTPUT_INTERVAL}间隔的站点潮位和300 m增水分布至{OUTPUT_DIRECTORY}，记录资料截止、延迟、模型身份和日志。

## 本实例输入槽
- {FORECAST_HORIZON} | required=True | type=str | var_name=预报时效 | hint=输入目标预报时效。 | default=未来3天
- {OUTPUT_INTERVAL} | required=True | type=str | var_name=输出时间间隔 | hint=输入产品时间间隔。 | default=1小时
- {OUTPUT_DIRECTORY} | required=True | type=str | var_name=结果输出目录 | hint=输入产品输出目录。 | default=None

## 本实例产出
- 风暴潮临近预报模型与配置
- 未来3天站点潮位和逐小时增水分布
- 实时资料状态、运行日志和产品清单

## 本实例质量门禁
- 每次推理只使用运行时刻前已获得的资料
- 实时缺测、延迟和降级均在产品质量标志中记录
- 站点与300 m网格产品覆盖未来3天且逐小时输出
- 模型、输入快照和运行日志可追溯

## 可调资源（edge:resource，仅真实存在）
- models/ensemble-model-output-statistics-emos-post-processing
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/wenhai-global-ocean-forecast-system

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
