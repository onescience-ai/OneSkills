# 骨架任务：海浪模型训练与多要素谱预报生成

- domain: climate
- 复用场景数: 1
- 实例任务数: 1

## 步骤描述（跨场景聚合去重）
- 利用地形、岸线、10 m风场和大区域边界生成综合波浪、风浪、涌浪及二维谱产品。

## 执行 prompt（跨场景聚合去重）
- 仅在s02任务配置冻结门禁和s03数据与干运行门禁均通过后执行；否则停止并标记BLOCKED。执行前核验本步骤全部输入值或路径已提供；对文件和数据类输入，核验其实际存在、可读、获准使用且与s03冻结的数据契约一致，并记录版本与校验信息；缺失或不一致时停止并标记BLOCKED。按s02冻结方案训练并冻结海浪模型，在{TRIAL_PERIOD}内按s02冻结的业务起报频次逐起报运行，生成每轮{FORECAST_HORIZON}、{OUTPUT_INTERVAL}间隔的综合波浪、风浪、涌浪和二维谱产品至{OUTPUT_DIRECTORY}；逐轮记录模型、驱动、边界、产品清单、缺报、失败与恢复情况。

## 输入槽（var/hint/default）
- {TRIAL_PERIOD} | required=True | type=str | var_name=试运行时段 | hint=输入连续试运行起止时间；时长须由s02冻结在1—2个月内。 | default=None
- {FORECAST_HORIZON} | required=True | type=str | var_name=预报时效 | hint=输入目标预报时效。 | default=不少于72小时
- {OUTPUT_INTERVAL} | required=True | type=str | var_name=输出时间间隔 | hint=输入产品时间间隔。 | default=1小时
- {OUTPUT_DIRECTORY} | required=True | type=str | var_name=结果输出目录 | hint=输入产品输出目录。 | default=None

## 产出
- 海浪智能预报模型与配置
- 连续试运行的综合波浪、风浪、涌浪和二维谱产品
- 逐起报驱动边界、缺报失败、恢复日志和产品索引

## 质量门禁 quality_gate
- 近岸和边界区域无未说明的断裂或异常增减幅
- 连续试运行覆盖s02冻结的1—2个月时段，各轮预报时效不少于72小时且输出间隔为1小时；缺报与失败均有记录
- 预报覆盖s02冻结的渤黄海网格和全部必需海浪产品
- 风场、地形与开放边界在每个有效时次正确对齐

## 可调资源（edge:resource，仅真实存在）
- models/ensemble-model-output-statistics-emos-post-processing
- tools/fengwu-global-medium-range-weather-forecast-system
- tools/wenhai-global-ocean-forecast-system

## 实例任务（本骨架在各场景的实例化）
- climate-wave-model-multi-element-bohai-yellow-sea-wave-inst

## 复用场景
- E106
