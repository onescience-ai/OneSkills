# 实例任务：独立评估与交付判定 @ E109

- domain: climate
- 骨架: tk-climate-b19b97a7
- 场景: sc-2c4fca50 (E109)
- step_id: s06
- depend: ['s05']

## 场景研究主体
- E109
- 关联论文: （源场景未提供）

## 本实例步骤描述
使用冻结的独立资料和同协议基线完成分层评估、试运行汇总、交付判定和复现归档。

## 本实例执行 prompt
{BASELINE_PRODUCTS}、{ACCEPTANCE_PROTOCOL}、{INUNDATION_METRIC}均为可选输入：未提供的规则或方案字段由agent依据s02冻结验收方案形成并留痕；未提供的外部数据、观测或基线不得由agent虚构，若它是完成产品或验收的必要依赖则停止并标记BLOCKED。使用{INDEPENDENT_VALIDATION_DATA}、{BASELINE_PRODUCTS}、{INUNDATION_METRIC}和{ACCEPTANCE_PROTOCOL}评估漫滩空间结果与运行时限；缺少精度门限时，不对空间性能指标判PASS。

## 本实例输入槽
- {INDEPENDENT_VALIDATION_DATA} | required=True | type=str | var_name=独立验证资料 | hint=输入独立验证资料路径。 | default=None
- {BASELINE_PRODUCTS} | required=False | type=str | var_name=同协议基线产品 | hint=输入基线产品路径。 | default=None
- {ACCEPTANCE_PROTOCOL} | required=False | type=str | var_name=验收协议 | hint=输入指标公式和门限。 | default=None
- {INUNDATION_METRIC} | required=False | type=str | var_name=淹没评估指标 | hint=输入空间评估公式。 | default=None

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
- （域内暂无匹配资源卡——资源缺口，不编造）

## 验收/缺失策略（继承场景）
- acceptance: （源场景未提供）
- missing_policy: （源场景未提供）
