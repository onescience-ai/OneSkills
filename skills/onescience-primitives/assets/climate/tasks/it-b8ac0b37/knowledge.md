# 实例任务：区域FourCastNet迁移训练与预报生成 @ E107

- domain: climate
- 骨架: tk-climate-cfea5a68
- 场景: sc-6771277f (E107)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E107
- 关联论文: （源场景未提供）

## 本实例步骤描述
完成渤黄海区域迁移训练、边界约束推理和逐小时多要素预报产品生成。

## 本实例执行 prompt
仅在s02任务配置冻结门禁和s03数据与干运行门禁均通过后执行；否则停止并标记BLOCKED。执行前核验本步骤全部输入值或路径已提供；对文件和数据类输入，核验其实际存在、可读、获准使用且与s03冻结的数据契约一致，并记录版本与校验信息；缺失或不一致时停止并标记BLOCKED。按s02冻结方案训练和微调区域FourCastNet，以{FORECAST_START_TIME}起报，生成{FORECAST_HORIZON}、{OUTPUT_INTERVAL}间隔的渤黄海预报产品至{OUTPUT_DIRECTORY}；记录边界使用、配置、模型身份、日志和异常。

## 本实例输入槽
- {FORECAST_START_TIME} | required=True | type=str | var_name=起报时间 | hint=输入UTC起报时间。 | default=None
- {FORECAST_HORIZON} | required=True | type=str | var_name=预报时效 | hint=输入目标预报时效。 | default=不少于72小时
- {OUTPUT_INTERVAL} | required=True | type=str | var_name=输出时间间隔 | hint=输入产品时间间隔。 | default=1小时
- {OUTPUT_DIRECTORY} | required=True | type=str | var_name=结果输出目录 | hint=输入产品输出目录。 | default=None

## 本实例产出
- 区域FourCastNet模型与配置
- 渤黄海逐小时大气预报场
- 边界约束记录、运行日志和产品清单

## 本实例质量门禁
- 模型输入输出与s02冻结的变量、网格和时间契约一致
- 大区域边界产品在每个有效时次被正确使用且无未说明断裂
- 训练、调参和推理配置身份可追溯
- 预报覆盖不少于72小时且输出间隔为1小时

## 可调资源（edge:resource，仅真实存在）
- models/fourcastnet

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
