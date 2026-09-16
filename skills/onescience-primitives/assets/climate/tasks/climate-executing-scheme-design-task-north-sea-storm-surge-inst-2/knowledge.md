# 实例任务：执行方案设计与任务配置冻结 @ E102

- domain: climate
- 骨架: climate-executing-scheme-design-task-configuration-freeze-task
- 场景: climate-north-sea-storm-surge-intelligent-correction-scenario (E102)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- E102
- 关联论文: 基于机器学习的广东海域模式风暴潮数据订正及评估 | doi:; 基于深度学习的潮位预报订正技术研究 | doi:; 长短期记忆神经网络（LSTM）对风暴潮数值模拟的优化应用 | doi:

## 本实例步骤描述
由agent根据预检结果形成方法、数据、资源、验证和失败分支方案，冻结任务范围、运行配置与验收口径。

## 本实例执行 prompt
围绕{OPERATIONAL_SCHEDULE}、{GPU_ENVIRONMENT}和{RESOURCE_BUDGET}形成订正方法、极端事件评估、部署和失败分支方案，定义s03最小干运行范围并冻结指标口径。将任务范围、数据契约、方法、资源、运行环境和验收协议写入版本化任务配置；关键字段无法冻结时标记BLOCKED，配置冻结后方可进入s03。

## 本实例输入槽
- {OPERATIONAL_SCHEDULE} | required=True | type=str | var_name=业务运行频次 | hint=输入每日运行时刻。 | default=每日两次
- {GPU_ENVIRONMENT} | required=True | type=str | var_name=目标GPU环境 | hint=输入GPU环境与调度信息。 | default=None
- {RESOURCE_BUDGET} | required=True | type=str | var_name=资源与时间预算 | hint=输入可用资源和期限。 | default=None

## 本实例产出
- 冻结的执行与验收方案
- 版本化任务配置
- 资源估算、风险和失败分支

## 本实例质量门禁
- 方案说明方法、数据和资源选择理由且未把实现细节冒充既定任务条件
- 必需数据、可选数据、获取责任和缺失时的阻断条件已列明
- 指标公式、基线、验证资料、样本范围和计时边界已列明
- 任务范围、配置口径和高成本工作边界已经由agent冻结并留存版本记录

## 可调资源（edge:resource，仅真实存在）
- datasets/sgp-c1-multi-source-boundary-layer-height-dataset
- tools/glo12v4-operational-ocean-forecasting-system

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
