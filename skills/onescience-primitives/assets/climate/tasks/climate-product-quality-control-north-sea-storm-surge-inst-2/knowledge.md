# 实例任务：产品质控与运行性能检查 @ E102

- domain: climate
- 骨架: climate-product-quality-control-operational-performance-check-task
- 场景: climate-north-sea-storm-surge-intelligent-correction-scenario (E102)
- step_id: s05
- depend: ['s04']

## 场景研究主体
- E102
- 关联论文: 基于机器学习的广东海域模式风暴潮数据订正及评估 | doi:; 基于深度学习的潮位预报订正技术研究 | doi:; 长短期记忆神经网络（LSTM）对风暴潮数值模拟的优化应用 | doi:

## 本实例步骤描述
检查产品完整性、物理与统计合理性、时空连续性、异常和目标GPU环境下的运行性能。

## 本实例执行 prompt
{PRODUCT_QC_SPEC}、{RUNTIME_PROTOCOL}均为可选输入：未提供的规则或方案字段由agent依据s02冻结方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。依据{PRODUCT_QC_SPEC}和{EXTREME_EVENT_THRESHOLD}检查站点与网格产品、潮位连续性、极端过程保持和异常，并按{RUNTIME_PROTOCOL}测量每日两次业务运行性能。

## 本实例输入槽
- {PRODUCT_QC_SPEC} | required=False | type=str | var_name=产品质控规格 | hint=输入产品质控规则。 | default=None
- {RUNTIME_PROTOCOL} | required=False | type=str | var_name=运行计时协议 | hint=输入硬件与计时边界。 | default=None
- {EXTREME_EVENT_THRESHOLD} | required=True | type=str | var_name=重点增水阈值 | hint=输入重点事件阈值。 | default=超过100cm

## 本实例产出
- 产品完整性与异常报告
- 物理和统计质控报告
- GPU运行性能报告

## 本实例质量门禁
- 产品变量、单位、坐标、有效时间和质量标志完整
- 缺测、重复、跳变、越界和不合理值已定位并记录
- 运行性能使用冻结后的目标硬件、数据规模和计时边界测量
- 质控失败的产品未进入正式验收样本

## 可调资源（edge:resource，仅真实存在）
- datasets/modis-myd13a3-ndvi-product
- datasets/snodas-swe-data-product
- models/dust-event-forecasting-with-multi-task-deep-learning
- models/dynamic-pre-training-for-time-series-dynpt
- models/importance-sampling-strategy-for-extreme-events
- tools/ecmwf-hres

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
