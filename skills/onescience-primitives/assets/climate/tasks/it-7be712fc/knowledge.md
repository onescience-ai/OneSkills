# 实例任务：海温订正降尺度模型训练与产品生成 @ E103

- domain: climate
- 骨架: tk-climate-202a71c7
- 场景: sc-e681786f (E103)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E103
- 关联论文: （源场景未提供）

## 本实例步骤描述
融合海温数值预报、海表观测和气象强迫，生成未来7天1 km逐小时三维海温产品。

## 本实例执行 prompt
仅在s02任务配置冻结门禁和s03数据与干运行门禁均通过后执行；否则停止并标记BLOCKED。执行前核验本步骤全部输入值或路径已提供；对文件和数据类输入，核验其实际存在、可读、获准使用且与s03冻结的数据契约一致，并记录版本与校验信息；缺失或不一致时停止并标记BLOCKED。按s02冻结方案训练并运行海温订正降尺度模型，以{FORECAST_START_TIME}生成{FORECAST_HORIZON}、{OUTPUT_INTERVAL}间隔的1 km三维海温产品至{OUTPUT_DIRECTORY}，保留原始—改进对应、模型身份和日志。

## 本实例输入槽
- {FORECAST_START_TIME} | required=True | type=str | var_name=起报时间 | hint=输入UTC起报时间。 | default=None
- {FORECAST_HORIZON} | required=True | type=str | var_name=预报时效 | hint=输入目标预报时效。 | default=未来7天
- {OUTPUT_INTERVAL} | required=True | type=str | var_name=输出时间间隔 | hint=输入产品时间间隔。 | default=1小时
- {OUTPUT_DIRECTORY} | required=True | type=str | var_name=结果输出目录 | hint=输入产品输出目录。 | default=None

## 本实例产出
- 海温订正与降尺度模型及权重
- 未来7天1km逐小时三维海温产品
- 原始—改进索引、日志和产品清单

## 本实例质量门禁
- 推理输入均在对应起报时刻可获得
- 输出覆盖未来7天、水平1 km、逐小时和s02冻结的全部垂向层次
- 细尺度结构具有独立高分辨率资料支持并通过质控
- 原始与改进产品在变量、深度、有效时刻和单位上可对应

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
