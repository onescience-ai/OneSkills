# 实例任务：三维温盐流联合模型训练与预报生成 @ E104

- domain: climate
- 骨架: tk-climate-0e437bce
- 场景: sc-40dcb436 (E104)
- step_id: s04
- depend: ['s03']

## 场景研究主体
- E104
- 关联论文: LangYa: a large AI model for global ocean forecasting | doi:

## 本实例步骤描述
将海水状态方程等物理约束嵌入神经网络，生成逐小时三维温度、盐度和海流预报。

## 本实例执行 prompt
仅在s02任务配置冻结门禁和s03数据与干运行门禁均通过后执行；否则停止并标记BLOCKED。执行前核验本步骤全部输入值或路径已提供；对文件和数据类输入，核验其实际存在、可读、获准使用且与s03冻结的数据契约一致，并记录版本与校验信息；缺失或不一致时停止并标记BLOCKED。按s02冻结方案训练并运行三维温盐流模型，以{FORECAST_START_TIME}生成{FORECAST_HORIZON}、{OUTPUT_INTERVAL}间隔的温度、盐度和海流产品至{OUTPUT_DIRECTORY}，记录物理约束诊断、模型身份和日志。

## 本实例输入槽
- {FORECAST_START_TIME} | required=True | type=str | var_name=起报时间 | hint=输入UTC起报时间。 | default=None
- {FORECAST_HORIZON} | required=True | type=str | var_name=预报时效 | hint=输入目标预报时效。 | default=7天
- {OUTPUT_INTERVAL} | required=True | type=str | var_name=输出时间间隔 | hint=输入产品时间间隔。 | default=1小时
- {OUTPUT_DIRECTORY} | required=True | type=str | var_name=结果输出目录 | hint=输入产品输出目录。 | default=None

## 本实例产出
- 三维温盐流智能预报模型与配置
- 逐小时三维温度盐度海流产品
- 物理诊断、运行日志和产品清单

## 本实例质量门禁
- 温度、盐度和海流全部按s02冻结网格与不少于30层输出
- 初始场、强迫和开放边界在每个有效时次正确对齐
- 物理约束实现和诊断结果可复核
- 预报覆盖s02冻结时效且输出间隔为1小时

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
