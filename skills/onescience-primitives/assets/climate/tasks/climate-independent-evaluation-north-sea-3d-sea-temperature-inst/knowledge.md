# 实例任务：独立评估与交付判定 @ E103

- domain: climate
- 骨架: climate-independent-evaluation-delivery-task
- 场景: climate-north-sea-3d-sea-temperature-smart-correction-and-downscaling-scenario (E103)
- step_id: s06
- depend: ['s05']

## 场景研究主体
- E103
- 关联论文: （源场景未提供）

## 本实例步骤描述
使用冻结的独立资料和同协议基线完成分层评估、试运行汇总、交付判定和复现归档。

## 本实例执行 prompt
{BASELINE_PRODUCTS}、{ACCEPTANCE_PROTOCOL}、{IMPROVEMENT_PROTOCOL}均为可选输入：未提供的规则或方案字段由agent依据s02冻结验收方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。使用{INDEPENDENT_VALIDATION_DATA}、{BASELINE_PRODUCTS}、{IMPROVEMENT_PROTOCOL}和{ACCEPTANCE_PROTOCOL}按深度、区域和提前期比较原预报与1 km产品，核验改善≥30%和表层误差。

## 本实例输入槽
- {INDEPENDENT_VALIDATION_DATA} | required=True | type=str | var_name=独立验证资料 | hint=输入独立验证资料路径。 | default=None
- {BASELINE_PRODUCTS} | required=False | type=str | var_name=同协议基线产品 | hint=输入基线产品路径。 | default=None
- {ACCEPTANCE_PROTOCOL} | required=False | type=str | var_name=验收协议 | hint=输入指标公式和门限。 | default=None
- {IMPROVEMENT_PROTOCOL} | required=False | type=str | var_name=海温改善协议 | hint=输入30%改善计算规则。 | default=None

## 本实例产出
- 分区域分变量分时效评估报告
- 基线比较与试运行报告
- 逐项验收判定与完整交付清单

## 本实例质量门禁
- 独立验证资料未参与训练、调参或阈值选择
- 模型与基线使用相同样本、区域、变量、网格和指标协议
- 每个性能结论均可定位到样本、公式、产品和日志证据
- 必要数据仍缺失或无法形成科学上可辩护唯一口径的项目未标记为PASS
- 源代码、模型、产品、文档和复现包均可重新读取

## 可调资源（edge:resource，仅真实存在）
- datasets/data-infrastructure-observations-and-labels
- datasets/gedi-footprint-canopy-height-data
- datasets/lpma-airport-wind-observation-validation
- datasets/modis-myd13a3-ndvi-product
- datasets/ostia-sst-data
- datasets/smap-level-3-passive-soil-moisture-products
- datasets/snodas-swe-data-product
- models/multivariate-data-fusion-vector-wind-prediction

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
