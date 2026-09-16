# 实例任务：执行方案设计与任务配置冻结 @ E106

- domain: climate
- 骨架: climate-executing-scheme-design-task-configuration-freeze-task
- 场景: climate-bohai-yellow-sea-wave-intelligent-forecast-scenario (E106)
- step_id: s02
- depend: ['s01']

## 场景研究主体
- E106
- 关联论文: Ocean Wave Forecasting With Deep Learning as Alternative to Conventional Models | doi:

## 本实例步骤描述
由agent根据预检结果形成方法、数据、资源、验证和失败分支方案，冻结任务范围、运行配置与验收口径。

## 本实例执行 prompt
{REFINEMENT_AREAS}均为可选输入：未提供的规则或方案字段由agent依据s01预检结果形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。结合{REFINEMENT_AREAS}、{GPU_ENVIRONMENT}和{RESOURCE_BUDGET}形成海浪预报、浅水与边界约束、二维谱、验证和部署方案，并定义s03最小干运行范围后冻结任务配置。将任务范围、数据契约、方法、资源、运行环境和验收协议写入版本化任务配置；关键字段无法冻结时标记BLOCKED，配置冻结后方可进入s03。

## 本实例输入槽
- {REFINEMENT_AREAS} | required=False | type=str | var_name=重点加密区域 | hint=输入岸线浴场渔场清单。 | default=None
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

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
