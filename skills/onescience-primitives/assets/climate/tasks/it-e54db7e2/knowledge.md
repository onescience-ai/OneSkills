# 实例任务：空间数据对齐与运行输入构建 @ E109

- domain: climate
- 骨架: tk-climate-04faed5a
- 场景: sc-2c4fca50 (E109)
- step_id: s03
- depend: ['s02']

## 场景研究主体
- E109
- 关联论文: （源场景未提供）

## 本实例步骤描述
按s02冻结方案对齐预测潮位、地形、岸线、防护工程和行政区划，构建运行输入与独立验证索引，并完成最小干运行。

## 本实例执行 prompt
仅在s02任务配置冻结门禁通过后执行。{DATA_ALIGNMENT_SPEC}、{SAMPLE_SPLIT_SPEC}均为可选输入：未提供的规则或方案字段由agent依据s02冻结方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。按{TERRAIN_COAST_DEFENSE}、{ADMINISTRATIVE_BOUNDARIES}、{DATA_ALIGNMENT_SPEC}和{SAMPLE_SPLIT_SPEC}对齐潮位与空间数据，检查高程基准、坐标、岸线、防护工程、行政边界和验证样本。完成对齐与样本构建后，运行s02冻结的最小案例，实际验证数据读取、核心计算或模型构建与加载、单批次前向或短流程以及结果写出，并保存输入快照、配置和日志；最小干运行不得作为精度或业务性能通过证据。

## 本实例输入槽
- {TERRAIN_COAST_DEFENSE} | required=True | type=str | var_name=地形岸线防护数据 | hint=输入s01核验通过的地形岸线工程路径。 | default=None
- {ADMINISTRATIVE_BOUNDARIES} | required=True | type=str | var_name=行政区划数据 | hint=输入s01核验通过的行政边界数据路径。 | default=None
- {DATA_ALIGNMENT_SPEC} | required=False | type=str | var_name=数据对齐规格 | hint=可输入已冻结对齐规则。 | default=None
- {SAMPLE_SPLIT_SPEC} | required=False | type=str | var_name=样本划分规格 | hint=可输入已冻结划分规则。 | default=None

## 本实例产出
- 对齐后的潮位与空间数据
- 运行输入与独立验证索引
- 数据质量、处理记录和最小干运行日志

## 本实例质量门禁
- 时间、空间、变量、单位和坐标语义一致
- 方法构建或配置、参数选择和独立验证资料用途隔离且无时间或空间泄漏
- 缺测、异常、插补和剔除均有记录，处理前后数据可追溯
- 最小干运行满足输入输出契约并无异常数值
- 模型、依赖、GPU环境和数据接口兼容
- 本步骤声明的全部必要外部数据、基础模型工件（如适用）和软件依赖均已实际获得、可读且版本冻结；只有获取方案而尚未取得本步骤必要输入时，本步骤不得通过

## 可调资源（edge:resource，仅真实存在）
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
