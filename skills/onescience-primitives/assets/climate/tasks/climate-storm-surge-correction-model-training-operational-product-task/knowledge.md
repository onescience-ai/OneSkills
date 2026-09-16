# 骨架任务：风暴潮订正模型训练与业务产品生成

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 利用当天预报、气象场、前日模拟和观测生成站点与网格风暴潮订正产品。

## 执行 prompt（跨场景聚合去重）
- 仅在s02任务配置冻结门禁和s03数据与干运行门禁均通过后执行；否则停止并标记BLOCKED。执行前核验本步骤全部输入值或路径已提供；对文件和数据类输入，核验其实际存在、可读、获准使用且与s03冻结的数据契约一致，并记录版本与校验信息；缺失或不一致时停止并标记BLOCKED。按s02冻结方案训练并冻结订正模型，对{TARGET_FORECAST_CYCLE}生成站点潮位曲线、逐小时300 m风暴增水分布和偏差场至{OUTPUT_DIRECTORY}，记录输入批次、模型身份和日志。

## 输入槽（var/hint/default）
- {TARGET_FORECAST_CYCLE} | required=True | type=str | var_name=待订正预报批次 | hint=输入当天预报批次路径。 | default=None
- {OUTPUT_DIRECTORY} | required=True | type=str | var_name=结果输出目录 | hint=输入产品输出目录。 | default=None

## 产出
- 原始—订正索引、日志和产品清单
- 站点潮位曲线和逐小时增水分布
- 风暴潮智能订正模型与权重

## 质量门禁 quality_gate
- >100 cm事件未被静默删除或平滑
- 推理输入均在对应业务起报时可获得
- 每日两次产品均有完整输入和模型身份记录
- 站点和300 m网格产品的有效时刻与单位一致

## 可调资源（edge:resource，仅真实存在）
- models/ensemble-model-output-statistics-emos-post-processing
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/wenhai-global-ocean-forecast-system

## 实例任务（本骨架在各场景的实例化）
- climate-storm-surge-correction-model-north-sea-storm-surge-inst

## 复用场景
- E102
